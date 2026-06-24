#core/utils.py
import logging
import threading
from django.template import loader
from django.conf import settings
from core.models import ConfiguracaoEmail
import os

# Tenta importar o SDK para não quebrar o sistema caso falte a biblioteca
try:
    import sib_api_v3_sdk
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

logger = logging.getLogger(__name__)

def _executar_envio_async(assunto, html_content, text_content, destinatarios):
    """Executa o envio real pela API HTTP em segundo plano na porta 443."""
    config_email = ConfiguracaoEmail.objects.first()
    
    # 1. Tenta pegar do painel Admin
    if config_email and config_email.senha_app:
        api_key = config_email.senha_app
        remetente_email = config_email.email_remetente
    else:
        # 2. Busca DIRETO das variáveis de ambiente (Railway / .env) com fallback para settings
        api_key = os.getenv('BREVO_API_KEY') or getattr(settings, 'BREVO_API_KEY', '')
        remetente_email = os.getenv('EMAIL_HOST_USER') or getattr(settings, 'EMAIL_HOST_USER', 'fepi.site@gmail.com')

    if SDK_AVAILABLE and api_key:
        try:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = api_key
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

            # Converte a lista de e-mails para o formato exigido pela Brevo
            to_list = [{"email": email} for email in destinatarios]

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to_list,
                sender={"name": "Federação Espírita Piauiense", "email": remetente_email},
                reply_to={"email": "naoresponder@fepi.org.br"},
                subject=assunto,
                html_content=html_content,
                text_content=text_content
            )
            
            api_instance.send_transac_email(send_smtp_email)
            logger.info(f"✅ E-mail transacional enviado via Brevo API para {destinatarios}")
        except Exception as e:
            logger.error(f"❌ Falha no disparo transacional Brevo ({destinatarios}). Erro: {str(e)}")
    else:
        print("================ DIAGNÓSTICO DE E-MAIL ================")
        print(f"1. Pacote SDK Instalado? {SDK_AVAILABLE}")
        print(f"2. Chave da API Encontrada? {bool(api_key)}")
        print("=======================================================")
        logger.error("❌ SDK da Brevo ou API Key não disponíveis para o disparo.")


def enviar_email_sistema(assunto, corpo, destinatarios, template_name=None, context=None):
    """
    Função coringa universal para disparar e-mails via Brevo API em segundo plano.
    Mantém compatibilidade com chamadas antigas (texto puro) e aceita Templates HTML.
    """
    try:
        html_content = None
        text_content = corpo 
        
        # Se um template HTML for informado, nós o renderizamos!
        if template_name and context:
            html_content = loader.render_to_string(template_name, context)
            text_content = None # Limpa o texto puro pois o HTML assume o comando
        elif "<html" in str(corpo).lower():
            # Pequena inteligência: Se mandarem código HTML direto no 'corpo', o sistema reconhece
            html_content = corpo
            text_content = None

        # Garante que 'destinatarios' seja sempre uma lista, mesmo se mandarem apenas uma string
        if isinstance(destinatarios, str):
            destinatarios = [destinatarios]

        # Dispara em Background (Thread) para a tela do administrador/usuário não congelar
        thread = threading.Thread(
            target=_executar_envio_async,
            args=(assunto, html_content, text_content, destinatarios)
        )
        thread.start()
        
        logger.info(f"Thread de e-mail criada para {destinatarios}")
        return True
    except Exception as e:
        logger.error(f"Erro ao preparar e-mail para {destinatarios}: {str(e)}")
        return False