from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.template import loader
from django.conf import settings
from core.models import ConfiguracaoEmail
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import logging
import os

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
    Formulário customizado para recuperação de senha que envia e-mails via SDK Oficial Brevo.
    Isso garante maior compatibilidade e melhores mensagens de erro.
    """
    
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Envia e-mail de recuperação de senha via SDK Oficial Brevo.
        """
        # 1. Busca as credenciais
        config_email = ConfiguracaoEmail.objects.first()
        if config_email and config_email.senha_app:
            api_key = config_email.senha_app
            remetente_email = config_email.email_remetente
        else:
            api_key = getattr(settings, 'BREVO_API_KEY', '')
            remetente_email = getattr(settings, 'EMAIL_HOST_USER', '')

        # Se não houver chave API, fallback imediato para o padrão do Django (SMTP)
        if not api_key:
            logger.warning(f"BREVO_API_KEY não encontrada. Usando fallback SMTP para {to_email}")
            super().send_mail(subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name)
            return

        # 2. Configura o SDK Brevo
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = api_key
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

        # 3. Prepara o conteúdo
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        html_content = loader.render_to_string(html_email_template_name, context) if html_email_template_name else body

        # 4. Cria o objeto de e-mail
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email}],
            reply_to={"email": "naoresponder@fepi.org.br"},
            sender={"name": "Federação Espírita Piauiense", "email": remetente_email},
            subject=subject,
            html_content=html_content
        )

        try:
            # 5. Tenta enviar via API
            api_response = api_instance.send_transac_email(send_smtp_email)
            logger.info(f"✅ E-mail enviado via Brevo SDK para {to_email}. ID: {api_response.message_id}")
        except ApiException as e:
            logger.error(f"❌ Erro Brevo SDK ({to_email}): {e}")
            # Se der erro 401, 403 ou qualquer outro na API, tentamos o SMTP
            try:
                logger.info(f"Iniciando fallback SMTP para {to_email}...")
                super().send_mail(subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name)
                logger.info(f"✅ Fallback SMTP funcionou para {to_email}")
            except Exception as smtp_err:
                logger.error(f"❌ Falha total: API e SMTP falharam para {to_email}. Erro SMTP: {str(smtp_err)}")
        except Exception as e:
            logger.error(f"❌ Erro inesperado no envio para {to_email}: {str(e)}")
            # Fallback genérico
            super().send_mail(subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name)
