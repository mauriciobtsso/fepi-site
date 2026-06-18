import os
import django
import sys

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fepi_site.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

def testar_smtp():
    print("\n--- 1. TESTANDO SMTP ---")
    try:
        print(f"Tentando enviar via {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...")
        print(f"Usuário: {settings.EMAIL_HOST_USER}")
        # Mascarar a senha para o log
        senha = settings.EMAIL_HOST_PASSWORD
        senha_mask = senha[:4] + "*" * (len(senha)-8) + senha[-4:] if len(senha) > 8 else "****"
        print(f"Senha: {senha_mask}")
        
        send_mail(
            'Teste de Diagnóstico FEPI',
            'Se você recebeu isso, o SMTP está funcionando!',
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        print("✅ SUCESSO: E-mail SMTP enviado!")
    except Exception as e:
        print(f"❌ FALHA: Erro no SMTP: {str(e)}")

def testar_api():
    print("\n--- 2. TESTANDO API HTTP (SDK) ---")
    api_key = getattr(settings, 'BREVO_API_KEY', '')
    if not api_key:
        print("❌ FALHA: BREVO_API_KEY não configurada no settings.py")
        return

    # Mascarar a chave para o log
    key_mask = api_key[:4] + "*" * (len(api_key)-8) + api_key[-4:] if len(api_key) > 8 else "****"
    print(f"Chave API: {key_mask}")

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": settings.EMAIL_HOST_USER}],
        sender={"name": "Diagnóstico FEPI", "email": settings.EMAIL_HOST_USER},
        subject="Teste de Diagnóstico API Brevo",
        html_content="<html><body><h1>Funciona!</h1><p>API Brevo via SDK está ok.</p></body></html>"
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(f"✅ SUCESSO: E-mail API enviado! ID: {api_response.message_id}")
    except ApiException as e:
        print(f"❌ FALHA: Erro na API Brevo (Status {e.status}):")
        print(f"Mensagem: {e.body}")
    except Exception as e:
        print(f"❌ FALHA: Erro inesperado: {str(e)}")

if __name__ == "__main__":
    print("🚀 INICIANDO DIAGNÓSTICO DE E-MAIL FEPI")
    testar_smtp()
    testar_api()
    print("\n--- FIM DO DIAGNÓSTICO ---")
