from django.db import models

# 1. Nova tabela para gerenciar Categorias Dinamicamente
class CategoriaDocumento(models.Model):
    nome = models.CharField("Nome da Categoria", max_length=100)
    
    class Meta:
        verbose_name = "Categoria de Documento"
        verbose_name_plural = "Categorias de Documentos"
    
    def __str__(self):
        return self.nome

# 2. Modelo de Documentos atualizado
class DocumentoRestrito(models.Model):
    titulo = models.CharField("Título do Documento", max_length=200)
    descricao = models.TextField("Descrição/Observação", blank=True, null=True)
    
    arquivo = models.FileField(upload_to='intranet_docs/', blank=True, null=True)
    link = models.URLField("Link Externo (Google Drive, etc)", blank=True, null=True)
    
    # Aqui está a mágica: Ligamos à tabela de cima (ForeignKey)
    # on_delete=models.PROTECT impede apagar uma categoria se ela tiver documentos
    categoria = models.ForeignKey(
        CategoriaDocumento, 
        on_delete=models.PROTECT, 
        verbose_name="Categoria",
        related_name="documentos"
    )
    
    data_publicacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento Restrito"
        verbose_name_plural = "Documentos Restritos (Intranet)"
        ordering = ['-data_publicacao']

    def __str__(self):
        return f"[{self.categoria.nome}] {self.titulo}"