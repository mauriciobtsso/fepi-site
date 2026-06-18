from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.template import loader
from django.conf import settings
from core.models import ConfiguracaoEmail
import logging
import threading

# Tenta importar o SDK, mas não quebra se não estiver instalado
try:
    import sib_api_v3_sdk
    from sib_api_v3_sdk.rest import ApiException
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

logger = logging.getLogger(__name__)

class ContatoForm(forms.Form):
    TOPICOS = [
        ('ATENDIMENTO', 'Atendimento Fraterno'),
        ('DUVIDA', 'Dúvida'),
        ('SUGESTAO', 'Sugestão / Melhoria'),
        ('CRITICA', 'Crítica'),
        ('DOACAO', 'Informações sobre Doação'),
    ]

    topico = forms.ChoiceField(
        choices=TOPICOS, 
        label="Assunto Principal", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    nome = forms.CharField(
        max_length=100, 
        label="Seu Nome Completo", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Maria da Silva'})
    )
    email = forms.EmailField(
        label="Seu Melhor E-mail", 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'})
    )
    mensagem = forms.CharField(
        label="Sua Mensagem", 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detalhe sua dúvida ou sugestão...'})
    )


class CustomPasswordResetForm(PasswordResetForm):
    """
    Formulário customizado para recuperação de senha.
    Envia e-mails em segundo plano (Background Thread) para evitar Timeout no Railway.
    """
    
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Inicia o envio do e-mail em uma thread separada.
        Isso faz o site responder instantaneamente ao usuário, enquanto o e-mail é enviado "por fora".
        """
        # Prepara os dados antes de disparar a thread (para evitar erros de contexto do Django)
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        html_content = loader.render_to_string(html_email_template_name, context) if html_email_template_name else body

        # Dispara o envio em segundo plano
        thread = threading.Thread(
            target=self._execute_send,
            args=(subject, body, html_content, to_email, subject_template_name, email_template_name, context, from_email, html_email_template_name)
        )
        thread.start()
        logger.info(f"Thread de envio iniciada para {to_email}")

def _execute_send(self, subject, body, html_content, to_email, *args):
        """
        Executa o envio real (dentro da thread).
        """
        # 1. Busca as credenciais dando prioridade à Chave de API correta
        config_email = ConfiguracaoEmail.objects.first()
        if config_email and config_email.senha_app:
            api_key = config_email.senha_app
            remetente_email = config_email.email_remetente
            logger.info(f"Usando credenciais do banco de dados para {to_email}")
        else:
            api_key = getattr(settings, 'BREVO_API_KEY', '')
            remetente_email = getattr(settings, 'EMAIL_HOST_USER', '')
            logger.info(f"Usando credenciais de ambiente para {to_email} (Remetente: {remetente_email})")
        
        # 2. Tenta via SDK Brevo (API HTTP) usando a porta 443 implícita
        if SDK_AVAILABLE and api_key:
            try:
                configuration = sib_api_v3_sdk.Configuration()
                configuration.api_key['api-key'] = api_key
                api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=[{"email": to_email}],
                    sender={"name": "Federação Espírita Piauiense", "email": remetente_email},
                    reply_to={"email": "naoresponder@fepi.org.br"}, # <-- Seu e-mail elegante adicionado aqui
                    subject=subject,
                    html_content=html_content
                )
                
                api_instance.send_transac_email(send_smtp_email)
                logger.info(f"✅ E-mail enviado via Brevo API para {to_email}")
                return # Sucesso!
            except Exception as e:
                logger.error(f"❌ Falha na API Brevo ({to_email}). Verifique se a chave de API (xkeysib) está correta. Detalhe: {str(e)}")

        # 3. Fallback para SMTP padrão do Django (Saberemos que falhará no Railway, mas fica de segurança para local)
        try:
            logger.info(f"Tentando fallback via SMTP para {to_email}...")
            super().send_mail(*args)
            logger.info(f"✅ E-mail enviado via SMTP Fallback para {to_email}")
        except Exception as smtp_err:
            logger.error(f"❌ Falha crítica: API e SMTP falharam para {to_email}. Erro SMTP: {str(smtp_err)}")