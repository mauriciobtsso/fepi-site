from django.db import models

class Centro(models.Model):
    TIPO_CHOICES = (
        ('CAPITAL', 'Capital (Teresina)'),
        ('INTERIOR', 'Interior do Estado'),
        ('ESPECIALIZADA', 'Entidade Especializada'),
    )

    ESTADO_CHOICES = (
        ('PI', 'Piauí'),
        ('MA', 'Maranhão'),
        ('CE', 'Ceará'),
    )

    # Identificação
    nome = models.CharField(max_length=200, verbose_name="Nome do Centro")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='CAPITAL')
    foto = models.ImageField(upload_to='centros/', blank=True, null=True, verbose_name="Logo")
    
    # Dados Jurídicos
    cnpj = models.CharField(max_length=20, blank=True, null=True, verbose_name="CNPJ")
    data_fundacao = models.DateField(blank=True, null=True, verbose_name="Data de Fundação")

    # Endereço
    cep = models.CharField(max_length=20, blank=True, null=True, verbose_name="CEP") # Aumentei para aceitar formatação se necessário
    endereco = models.CharField(max_length=300, verbose_name="Logradouro")
    numero = models.CharField(max_length=20, blank=True, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100, default="Teresina")
    estado = models.CharField(max_length=2, choices=ESTADO_CHOICES, default='PI')
    
    # Contatos
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    site = models.URLField(blank=True, null=True, verbose_name="Site ou Instagram") # <-- VOLTOU!
    
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Centro Espírita"
        verbose_name_plural = "Centros Espíritas"
        ordering = ['cidade', 'nome']