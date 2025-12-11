from django.db import models

class DocumentoRestrito(models.Model):
    CATEGORIAS = [
        ('ATA', 'Ata de Reunião'),
        ('CIRCULAR', 'Circular / Comunicado'),
        ('FINANCEIRO', 'Relatório Financeiro'),
        ('ADMIN', 'Documento Administrativo'),
        ('OUTROS', 'Outros'),
    ]

    titulo = models.CharField("Título do Documento", max_length=200)
    descricao = models.TextField("Descrição/Observação", blank=True, null=True)
    arquivo = models.FileField(upload_to='intranet_docs/')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='OUTROS')
    data_publicacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento Restrito"
        verbose_name_plural = "Documentos Restritos (Intranet)"
        ordering = ['-data_publicacao']

    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.titulo}"