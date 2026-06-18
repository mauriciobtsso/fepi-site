from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.template import loader
from django.conf import settings
from core.models import ConfiguracaoEmail
import urllib.request
import urllib.error
import json
import logging

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
    Formulário customizado para recuperação de senha que envia e-mails via API HTTP Brevo.
    Isso evita bloqueios de firewall em portas SMTP tradicionais (25, 587, 465).
    """
    
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Envia e-mail de recuperação de senha via API HTTP Brevo (Porta 443).
        """
        try:
            # 1. Prepara o Assunto e o Corpo HTML
            subject = loader.render_to_string(subject_template_name, context)
            subject = ''.join(subject.splitlines())
            body = loader.render_to_string(email_template_name, context)
            
            html_email = None
            if html_email_template_name is not None:
                html_email = loader.render_to_string(html_email_template_name, context)

            # 2. Busca as credenciais (Prioriza: Banco de Dados > Variáveis de Ambiente)
            config_email = ConfiguracaoEmail.objects.first()
            
            if config_email and config_email.senha_app:
                # Usa credenciais do painel administrativo
                api_key = config_email.senha_app
                remetente_email = config_email.email_remetente
                logger.info(f"Usando credenciais do banco de dados para {to_email}")
            else:
                # Usa variáveis de ambiente (settings.py)
                api_key = getattr(settings, 'BREVO_API_KEY', '')
                remetente_email = getattr(settings, 'EMAIL_HOST_USER', '')
                logger.info(f"Usando credenciais de ambiente para {to_email}")

            # 3. Valida se a chave API está configurada
            if not api_key:
                logger.error("BREVO_API_KEY não configurada em settings ou variáveis de ambiente")
                # Se não houver chave API, tentamos o envio padrão do Django (SMTP) como fallback
                super().send_mail(subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name)
                return
            
            # 4. Prepara a requisição para API HTTP Brevo (Porta 443 - Imbloqueável)
            url = "https://api.brevo.com/v3/smtp/email"
            
            payload = {
                "sender": {"name": "Federação Espírita Piauiense", "email": remetente_email},
                "to": [{"email": to_email}],
                "replyTo": {"email": "naoresponder@fepi.org.br"},
                "subject": subject,
                "htmlContent": html_email if html_email else body
            }

            data = json.dumps(payload).encode('utf-8')
            
            req = urllib.request.Request(url, data=data, headers={
                'accept': 'application/json',
                'api-key': api_key,
                'content-type': 'application/json'
            })

            # 5. Executa a chamada
            with urllib.request.urlopen(req, timeout=10) as response:
                logger.info(f"✅ E-mail enviado com sucesso para {to_email} via Brevo API")
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar e-mail via API Brevo: {str(e)}")
            # Fallback para o método padrão do Django (SMTP) caso a API falhe
            logger.info("Tentando fallback via SMTP padrão...")
            super().send_mail(subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name)
