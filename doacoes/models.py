from django.db import models
from ckeditor.fields import RichTextField

class PaginaDoacaoConfig(models.Model):
    """ Configuração Única (Singleton) para a página pública de doações """
    titulo_principal = models.CharField("Título Principal", max_length=200, default="Apoie a Causa Espírita")
    texto_apelo = RichTextField("Texto de Apelo", default="Sua doação é fundamental para mantermos nossas atividades.")
    imagem_capa = models.ImageField("Imagem de Destaque", upload_to='doacoes/capas/', blank=True, null=True)
    
    # Seção Sócio Contribuinte
    titulo_socio = models.CharField("Título da Seção Sócio", max_length=200, default="Seja um Sócio Contribuinte")
    texto_socio = RichTextField("Texto sobre ser Sócio", blank=True, null=True, help_text="Explique a importância, valores sugeridos, etc.")
    link_socio = models.URLField("Link Externo para Formulário de Sócio (Opcional)", blank=True, null=True)

    class Meta:
        verbose_name = "Configuração da Página de Doações"
        
    def __str__(self):
        return "Configuração da Página de Doações"


class FormaDoacao(models.Model):
    TIPO_CHOICES = (
        ('PIX', 'Pix (Chave)'),
        ('CONTA', 'Depósito/Transferência'),
        ('OUTRO', 'Outro Método/Link')
    )

    titulo = models.CharField(max_length=150, verbose_name="Título da Forma de Doação")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='PIX', verbose_name="Tipo")
    descricao = models.TextField(verbose_name="Instruções ou Descrição")
    
    chave_pix = models.CharField(max_length=200, blank=True, verbose_name="Chave PIX ou Código")
    qr_code = models.ImageField(upload_to='pix_qrcodes/', blank=True, null=True, verbose_name="QR Code (Imagem PNG/JPG)")
    
    banco = models.CharField(max_length=100, blank=True)
    agencia = models.CharField(max_length=20, blank=True)
    conta = models.CharField(max_length=30, blank=True, verbose_name="Conta / Favorecido")
    
    ordem = models.IntegerField(default=1)

    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name = "Forma de Doação"
        verbose_name_plural = "Formas de Doação"
        ordering = ['ordem']