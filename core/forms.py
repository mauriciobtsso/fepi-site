from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template import loader
from django.conf import settings
from core.models import ConfiguracaoEmail

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

        # 2. Busca as credenciais do Painel (Banco de Dados)
        config_email = ConfiguracaoEmail.objects.first()
        
        if config_email and config_email.senha_app:
            # Configura a máscara do remetente dinâmico
            remetente_formatado = f"Federação Espírita Piauiense <{config_email.email_remetente}>"
            
            connection = get_connection(
                host='smtp.gmail.com',      # <-- Nome oficial exigido pelo SSL do Google
                port=465,                   # <-- Nova porta do Google (SSL)
                username=config_email.email_remetente,
                password=config_email.senha_app,
                use_ssl=True,               # <-- Ativamos o SSL implícito
                use_tls=False,              # <-- Desligamos o TLS
                timeout=10
            )
        else:
            # Fallback de segurança para o settings.py caso o painel esteja vazio
            remetente_formatado = f"Federação Espírita Piauiense <{settings.DEFAULT_FROM_EMAIL}>"
            connection = get_connection(
                host='smtp.gmail.com',
                port=465,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_ssl=True,
                use_tls=False,
                timeout=10
            ) 

        # 3. Monta a mensagem aplicando o remetente elegante e e-mail de resposta
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=remetente_formatado,
            to=[to_email],
            reply_to=['naoresponder@fepi.org.br']
        )

        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        # 4. Dispara o e-mail com proteção anti-crash
        email_message.connection = connection
        try:
            email_message.send()
        except Exception as e:
            # Falha silenciosamente para o usuário não ver o Erro 500
            print(f"CRÍTICO: Falha ao enviar e-mail de recuperação. Motivo: {e}")