from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.template import loader
from django.conf import settings
from core.models import ConfiguracaoEmail
import urllib.request
import json

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
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        
        # 1. Prepara o Assunto e o Corpo HTML
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        
        html_email = None
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)

        # 2. Busca as credenciais do Painel (Banco de Dados)
        config_email = ConfiguracaoEmail.objects.first()
        
        if config_email and config_email.senha_app:
            api_key = config_email.senha_app
            remetente_email = config_email.email_remetente
        else:
            api_key = settings.EMAIL_HOST_PASSWORD
            remetente_email = settings.EMAIL_HOST_USER

        # -------------------------------------------------------------
        # A ARMA NUCLEAR: Disparo via API HTTP (Porta 443 - Imbloqueável)
        # -------------------------------------------------------------
        url = "https://api.brevo.com/v3/smtp/email"
        
        # Estrutura de dados exigida pela Brevo API
        payload = {
            "sender": {"name": "Federação Espírita Piauiense", "email": remetente_email},
            "to": [{"email": to_email}],
            "replyTo": {"email": "naoresponder@fepi.org.br"},
            "subject": subject,
            "htmlContent": html_email if html_email else body
        }

        # Converte para JSON
        data = json.dumps(payload).encode('utf-8')
        
        # Prepara a requisição de saída
        req = urllib.request.Request(url, data=data, headers={
            'accept': 'application/json',
            'api-key': api_key, # A chave xkeysib que você colocou no painel
            'content-type': 'application/json'
        })

        # 3. Executa a chamada
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                print("SUCESSO: E-mail enviado perfeitamente via API HTTP da Brevo!")
        except Exception as e:
            print(f"CRÍTICO: Falha API Brevo. Motivo: {e}")