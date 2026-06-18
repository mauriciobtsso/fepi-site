from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template import loader
from django.conf import settings
from core.models import ConfiguracaoEmail
import socket  # <-- NOVO IMPORT NECESSÁRIO PARA BURLAR O BLOQUEIO DO RAILWAY

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
        
        # 1. Prepara o Assunto e o Corpo usando o padrão do Django
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        # -------------------------------------------------------------
        # A MÁGICA: Forçar o IPv4 para burlar o bloqueio do Railway
        # -------------------------------------------------------------
        try:
            # Pega o IP numérico exato (IPv4) em vez do nome 'smtp.gmail.com'
            gmail_host_ipv4 = socket.gethostbyname('smtp.gmail.com')
        except socket.gaierror:
            # Fallback de segurança se o DNS falhar
            gmail_host_ipv4 = 'smtp.gmail.com'

        # 2. A NOSSA MÁGICA: Busca as credenciais do Painel (Banco de Dados)
        config_email = ConfiguracaoEmail.objects.first()
        
        if config_email and config_email.senha_app:
            connection = get_connection(
                host=gmail_host_ipv4,  # <-- USAMOS O IP RESOLVIDO AQUI
                port=587,
                username=config_email.email_remetente,
                password=config_email.senha_app,
                use_tls=True,
                timeout=10  # <-- PROTEÇÃO: Aborta se o Google demorar mais de 10s
            )
            email_message.from_email = config_email.email_remetente
        else:
            # Fallback de segurança para o settings.py
            connection = get_connection(
                host=gmail_host_ipv4,  # <-- AQUI TAMBÉM NO FALLBACK
                timeout=10
            ) 
            email_message.from_email = settings.DEFAULT_FROM_EMAIL

        # 3. Dispara o e-mail com proteção anti-crash
        email_message.connection = connection
        try:
            email_message.send()
        except Exception as e:
            # Falha silenciosamente para o usuário não ver o Erro 500
            print(f"CRÍTICO: Falha ao enviar e-mail de recuperação. Motivo: {e}")