from django.core.mail import send_mail, get_connection
from django.conf import settings
from core.models import ConfiguracaoEmail

def enviar_email_sistema(assunto, corpo, destinatarios):
    """
    Função coringa para disparar e-mails usando a configuração do painel.
    """
    config_email = ConfiguracaoEmail.objects.first()
    
    if config_email and config_email.senha_app:
        connection = get_connection(
            host='smtp.gmail.com',
            port=587,
            username=config_email.email_remetente,
            password=config_email.senha_app,
            use_tls=True
        )
        remetente = config_email.email_remetente
    else:
        # Fallback para o settings.py caso o painel esteja vazio
        connection = get_connection()
        remetente = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(
            assunto, 
            corpo, 
            remetente, 
            destinatarios, 
            connection=connection, 
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False