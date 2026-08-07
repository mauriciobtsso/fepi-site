from django.db import models

# 1. Nova tabela para gerenciar Categorias Dinamicamente
class CategoriaDocumento(models.Model):
    # CORREÇÃO: Limite de 100 aumentado para 255 para comportar nomes maiores de secretarias/departamentos
    nome = models.CharField("Nome da Categoria", max_length=255)
    
    class Meta:
        verbose_name = "Categoria de Documento"
        verbose_name_plural = "Categorias de Documentos"
    
    def __str__(self):
        return self.nome

# 2. Modelo de Documentos atualizado
class DocumentoRestrito(models.Model):
    # CORREÇÃO: Limite de 200 aumentado para 500 para suportar nomes extensos de arquivos de licitação e PDFs longos
    titulo = models.CharField("Título do Documento", max_length=500)
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