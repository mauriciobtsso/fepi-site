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
        
        # 1. Prepara o Assunto e o Corpo
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        # 2. Busca as credenciais do Painel
        config_email = ConfiguracaoEmail.objects.first()
        
        # --- CONFIGURAÇÕES FIXAS DA BREVO ---
        BREVO_HOST = 'smtp-relay.brevo.com'
        BREVO_PORT = 587
        BREVO_LOGIN = 'af2580001@smtp-brevo.com' # <-- Seu login de infraestrutura
        
        if config_email and config_email.senha_app:
            # O remetente que o usuário vai ver (vem do painel)
            remetente_formatado = f"Federação Espírita Piauiense <{config_email.email_remetente}>"
            
            connection = get_connection(
                host=BREVO_HOST,
                port=BREVO_PORT,
                username=BREVO_LOGIN,                  # <-- Login da Brevo
                password=config_email.senha_app,       # <-- Senha SMTP (vem do painel)
                use_tls=True,
                use_ssl=False,
                timeout=10
            )
        else:
            # Fallback
            remetente_formatado = f"Federação Espírita Piauiense <{settings.DEFAULT_FROM_EMAIL}>"
            connection = get_connection(
                host=BREVO_HOST,
                port=BREVO_PORT,
                username=BREVO_LOGIN,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=True,
                use_ssl=False,
                timeout=10
            ) 

        # 3. Monta a mensagem
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

        # 4. Dispara o e-mail
        email_message.connection = connection
        try:
            email_message.send()
        except Exception as e:
            print(f"CRÍTICO: Falha ao enviar e-mail pela Brevo. Motivo: {e}")