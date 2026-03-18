from django.db import models

class FormaDoacao(models.Model):
    TIPO_CHOICES = (
        ('PIX', 'Pix (Chave)'),
        ('CONTA', 'Depósito/Transferência'),
        ('OUTRO', 'Outro Método/Link')
    )

    titulo = models.CharField(max_length=150, verbose_name="Título da Forma de Doação")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='PIX', verbose_name="Tipo")
    descricao = models.TextField(verbose_name="Instruções ou Descrição")
    
    # Detalhes de Pagamento
    chave_pix = models.CharField(max_length=200, blank=True, verbose_name="Chave PIX ou Código")
    
    # NOVO CAMPO PARA A IMAGEM DO QR CODE
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