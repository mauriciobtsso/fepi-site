import json
import logging
import re
import time
from functools import lru_cache
from html import unescape
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.html import strip_tags
from google import genai as google_genai
from groq import Groq


logger = logging.getLogger(__name__)


PROMPT_BASE = """Você é o Assistente Executivo de Inteligência Artificial da Federação Espírita Piauiense (FEPI). Você ajuda administradores, secretários, diretores e redatores a utilizar o painel do site, redigir conteúdos e compreender os fluxos internos.

CONTEXTO INSTITUCIONAL DA FEPI:
- Instagram: https://www.instagram.com/fepiaui/
- Facebook: https://www.facebook.com/fepiaui
- Site oficial: https://fepiaui.org.br/
- Endereço: Rua Olavo Bilac, 1394 - Centro - Teresina - PI - CEP: 64001-280
- Telefone: (86) 3221-2500

REGRAS DE CONTEÚDO:
1. Para notícia, responda com TÍTULO, RESUMO de até 250 caracteres e CONTEÚDO.
2. Para evento, responda com TÍTULO e DESCRIÇÃO detalhada, incluindo data, horário e convite à participação.
3. Para coluna ou artigo, responda com TÍTULO, RESUMO de até 300 caracteres e CONTEÚDO.
4. Para o Editor.js: texto normal é digitado diretamente; subtítulo usa Heading; imagem usa Image; vídeo do YouTube usa Embed; citação usa Quote; lista usa List; linha divisória usa Delimiter. O menu também pode ser aberto com + ou pela tecla TAB.

DIRETRIZES DE RESPOSTA:
- Responda em Português do Brasil, com clareza, cordialidade e objetividade.
- Não use jargões religiosos exagerados nem saudações longas.
- Prefira instruções numeradas quando explicar um procedimento do painel.
- Não invente telas, links, valores, permissões, pagamentos, status ou funcionalidades que não estejam no contexto fornecido.
- Não solicite, repita ou revele tokens, chaves privadas, senhas, dados de cartão ou segredos de webhook.
- Em dúvidas financeiras, diferencie o que já existe do que está planejado e recomende conferir o registro interno quando a pergunta depender de um dado individual.
"""


TERMOS_FINANCEIROS = (
    "finance", "mensal", "plano", "adesão", "adesao", "cobrança", "cobranca",
    "pagamento", "pagar", "boleto", "pix", "gateway", "pagbank", "pagar.me",
    "inadimpl", "doador", "doação", "doacao", "federado", "associado",
    "webhook", "conciliação", "conciliacao", "relatório financeiro", "relatorio financeiro",
)


@lru_cache(maxsize=1)
def _manual_financeiro_texto():
    """Carrega o mesmo conteúdo apresentado na página interna do manual."""
    caminho = Path(settings.BASE_DIR) / "painel" / "templates" / "painel" / "financeiro" / "manual_conteudo.html"
    try:
        conteudo = caminho.read_text(encoding="utf-8")
        conteudo = re.sub(r"<\s*(br\s*/?|/(?:p|li|h[1-6]|tr|section|div))\s*>", "\n", conteudo, flags=re.IGNORECASE)
        conteudo = re.sub(r"<\s*/(?:td|th)\s*>", "\t", conteudo, flags=re.IGNORECASE)
        texto = unescape(strip_tags(conteudo))
        texto = re.sub(r"[ \t]+\n", "\n", texto)
        texto = re.sub(r"\n{3,}", "\n\n", texto)
        return texto.strip()
    except OSError:
        logger.exception("Não foi possível carregar o manual financeiro para o assistente.")
        return "O manual financeiro interno não está disponível neste momento. Não invente procedimentos financeiros; informe a limitação e oriente o administrador a consultar a equipe responsável."


def _pergunta_financeira(texto):
    texto_normalizado = texto.casefold()
    return any(termo in texto_normalizado for termo in TERMOS_FINANCEIROS)


def _prompt_sistema(mensagem_usuario):
    if not _pergunta_financeira(mensagem_usuario):
        return PROMPT_BASE

    return (
        f"{PROMPT_BASE}\n\n"
        "BASE DE CONHECIMENTO INTERNA — MANUAL DO MÓDULO FINANCEIRO:\n"
        f"{_manual_financeiro_texto()}\n\n"
        "Use o manual acima como fonte prioritária para perguntas financeiras. "
        "Se a pergunta exigir um dado individual que não esteja no texto, explique que o assistente não consulta registros privados nessa conversa e indique a tela administrativa apropriada. "
        "Não transforme uma função futura em função já disponível."
    )


def _texto_gemini(response):
    texto = getattr(response, "text", None)
    if not texto or not texto.strip():
        raise RuntimeError("O Gemini retornou uma resposta vazia.")
    return texto.strip()


def _texto_groq(response):
    escolhas = getattr(response, "choices", None) or []
    if not escolhas or not getattr(escolhas[0], "message", None):
        raise RuntimeError("O Groq retornou uma resposta vazia.")
    texto = getattr(escolhas[0].message, "content", None)
    if not texto or not texto.strip():
        raise RuntimeError("O Groq retornou uma resposta vazia.")
    return texto.strip()


@login_required
def chat_assistente_ia(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido."}, status=405)

    if len(request.body) > 64 * 1024:
        return JsonResponse({"erro": "A mensagem excede o limite permitido de 64 KB."}, status=413)

    try:
        data = json.loads(request.body or b"{}")
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({"erro": "Envie uma mensagem em formato JSON válido."}, status=400)

    mensagem_usuario = data.get("mensagem", "")
    if not isinstance(mensagem_usuario, str):
        return JsonResponse({"erro": "A mensagem precisa ser um texto."}, status=400)

    mensagem_usuario = mensagem_usuario.strip()
    limite_mensagem = max(500, int(getattr(settings, "AI_MAX_MESSAGE_CHARS", 4000)))
    if not mensagem_usuario:
        return JsonResponse({"erro": "Mensagem vazia."}, status=400)
    if len(mensagem_usuario) > limite_mensagem:
        return JsonResponse({"erro": f"A mensagem deve ter no máximo {limite_mensagem} caracteres."}, status=413)

    prompt_sistema = _prompt_sistema(mensagem_usuario)
    erros = []
    inicio = time.monotonic()
    chave_gemini = getattr(settings, "GEMINI_API_KEY", "")
    chave_groq = getattr(settings, "GROQ_API_KEY", "")

    if chave_gemini:
        try:
            client_google = google_genai.Client(
                api_key=chave_gemini,
                http_options={
                    "timeout": getattr(settings, "GEMINI_TIMEOUT_MS", 30000),
                    "retry_options": {
                        "attempts": getattr(settings, "GEMINI_MAX_RETRIES", 2),
                        "initial_delay": 0.5,
                        "max_delay": 3.0,
                    },
                },
            )
            response = client_google.models.generate_content(
                model=getattr(settings, "GEMINI_MODEL", "gemini-3-flash-preview"),
                contents=f"{prompt_sistema}\n\nMENSAGEM DO USUÁRIO:\n{mensagem_usuario}",
            )
            resposta = _texto_gemini(response)
            logger.info("Assistente IA respondeu via Gemini para usuário=%s em %.2fs", request.user.pk, time.monotonic() - inicio)
            return JsonResponse({"resposta": resposta, "provedor": "gemini"})
        except Exception as exc:
            erros.append("gemini")
            logger.warning("Falha controlada no Gemini para usuário=%s: %s", request.user.pk, type(exc).__name__)

    if chave_groq:
        try:
            client_groq = Groq(
                api_key=chave_groq,
                timeout=getattr(settings, "GROQ_TIMEOUT_SECONDS", 25.0),
                max_retries=getattr(settings, "GROQ_MAX_RETRIES", 1),
            )
            chat_completion = client_groq.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": mensagem_usuario},
                ],
                model=getattr(settings, "GROQ_MODEL", "openai/gpt-oss-20b"),
                max_tokens=1400,
                temperature=0.2,
            )
            resposta = _texto_groq(chat_completion)
            logger.info("Assistente IA respondeu via Groq para usuário=%s em %.2fs; fallback=%s", request.user.pk, time.monotonic() - inicio, bool(erros))
            return JsonResponse({"resposta": resposta, "provedor": "groq", "fallback": bool(erros)})
        except Exception as exc:
            erros.append("groq")
            logger.warning("Falha controlada no Groq para usuário=%s: %s", request.user.pk, type(exc).__name__)

    if not chave_gemini and not chave_groq:
        logger.error("Assistente IA sem credenciais configuradas para usuário=%s", request.user.pk)
    else:
        logger.error("Todos os provedores do assistente falharam para usuário=%s; provedores=%s", request.user.pk, ",".join(erros))
    return JsonResponse({"erro": "O assistente está temporariamente indisponível. Tente novamente em alguns instantes."}, status=503)
