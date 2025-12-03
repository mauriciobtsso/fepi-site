from django.db import models

class Centro(models.Model):
    # Opções para o filtro
    TIPO_CHOICES = (
        ('CAPITAL', 'Capital (Teresina)'),
        ('INTERIOR', 'Interior do Estado'),
        ('ESPECIALIZADA', 'Entidade Especializada'),
    )

    nome = models.CharField(max_length=200, verbose_name="Nome do Centro")
    endereco = models.CharField(max_length=300, verbose_name="Endereço Completo")
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, default="Teresina")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone/WhatsApp")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='CAPITAL')
    foto = models.ImageField(upload_to='centros/', blank=True, null=True, verbose_name="Foto ou Logo")
    
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Centro Espírita"
        verbose_name_plural = "Centros Espíritas"
        ordering = ['cidade', 'nome']