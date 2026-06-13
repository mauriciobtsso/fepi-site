import json
from google import genai as google_genai
from groq import Groq
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def chat_assistente_ia(request):
    """
    Endpoint com sistema de fallback automático: tenta Gemini primeiro pelo tom,
    se falhar aciona o Groq (Llama 3.1) como plano B estável.
    Contém Injeção de Contexto da FEPI e Regras Estruturais de Conteúdo.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mensagem_usuario = data.get('mensagem', '')

            if not mensagem_usuario:
                return JsonResponse({'erro': 'Mensagem vazia'}, status=400)

            # ==========================================
            # SUPER PROMPT (REGRAS E CONTEXTO DA FEPI)
            # ==========================================
            prompt_base = (
                "Você é o Assistente Executivo de Inteligência Artificial da Federação Espírita Piauiense (FEPI). "
                "Sua função principal é redigir, estruturar e revisar conteúdos para o site da instituição de forma ágil.\n\n"
                
                "DADOS INSTITUCIONAIS DA FEPI (Incorpore aos textos quando fizer sentido ou quando solicitado):\n"
                "- Instagram: https://www.instagram.com/fepiaui/\n"
                "- Facebook: https://www.facebook.com/fepiaui\n"
                "- Site Oficial: http://fepiaui.org.br/site/\n"
                "- Endereço: Rua Olavo Bilac, 1394 - Centro - Teresina - PI - CEP: 64001-280\n"
                "- Telefone/Contato: (86) 3221-2500\n\n"
                
                "REGRAS ESTRUTURAIS OBRIGATÓRIAS PARA CRIAÇÃO DE CONTEÚDO:\n"
                "1. QUANDO FOR NOTÍCIA: Você DEVE retornar a estrutura com:\n"
                "   - TÍTULO:\n"
                "   - RESUMO: (rigorosamente até 250 caracteres)\n"
                "   - CONTEÚDO: (o texto completo da notícia).\n"
                "2. QUANDO FOR EVENTO: Você DEVE retornar a estrutura com:\n"
                "   - TÍTULO:\n"
                "   - DESCRIÇÃO: (detalhada, incluindo datas, horários e apelos de participação).\n"
                "3. QUANDO FOR COLUNA/ARTIGO: Você DEVE retornar a estrutura com:\n"
                "   - TÍTULO:\n"
                "   - RESUMO: (rigorosamente até 300 caracteres)\n"
                "   - CONTEÚDO: (texto completo do artigo reflexivo ou doutrinário).\n\n"
                
                "DIRETRIZES DE TOM E ESTILO:\n"
                "- Responda em Português do Brasil natural, fluente e simpático.\n"
                "- Seja prático, direto e moderno. Vá direto ao ponto.\n"
                "- NÃO seja 'meloso' e NÃO utilize jargões religiosos exagerados ou saudações doutrinárias longas.\n"
                "- Nunca utilize traduções literais estranhas (ex: use sempre 'Rodas de Conversa' e nunca 'rondas')."
            )

            # ------------------------------------------------------------
            # TENTATIVA 1: GOOGLE GEMINI (Tom ideal do painel)
            # ------------------------------------------------------------
            chave_gemini = getattr(settings, 'GEMINI_API_KEY', None)
            if chave_gemini:
                try:
                    client_google = google_genai.Client(api_key=chave_gemini)

                    response = client_google.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=f"{prompt_base}\n\nMENSAGEM DO USUÁRIO: {mensagem_usuario}"
                    )
                    
                    return JsonResponse({'resposta': response.text})
                    
                except Exception as e_google:
                    print(f"[IA FEPI] Gemini instável ({str(e_google)}). Acionando plano B (Groq)...")
                    pass

            # ------------------------------------------------------------
            # TENTATIVA 2 (FALLBACK): GROQ LLAMA 3.1 (Estabilidade máxima)
            # ------------------------------------------------------------
            chave_groq = getattr(settings, 'GROQ_API_KEY', None)
            if not chave_groq:
                return JsonResponse({'erro': 'O serviço de inteligência artificial está temporariamente indisponível.'}, status=500)

            client_groq = Groq(api_key=chave_groq)
            modelo_groq = getattr(settings, 'GROQ_MODEL', 'llama-3.1-8b-instant')

            chat_completion = client_groq.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt_base},
                    {"role": "user", "content": mensagem_usuario}
                ],
                model=modelo_groq,
            )
            
            resposta_groq = chat_completion.choices[0].message.content
            return JsonResponse({'resposta': resposta_groq})

        except Exception as e:
            erro_str = str(e)
            if '503' in erro_str or 'UNAVAILABLE' in erro_str:
                msg_amigavel = "Puxa, meus servidores estão um pouco sobrecarregados neste exato segundo! Poderia tentar enviar sua mensagem de novo em alguns instantes?"
                return JsonResponse({'erro': msg_amigavel}, status=503)
            return JsonResponse({'erro': f'Ocorreu um erro geral de comunicação com o assistente: {erro_str}'}, status=500)
            
    return JsonResponse({'erro': 'Método não permitido'}, status=405)