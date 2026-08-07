from django.db import models
# Storage exclusivo da Intranet: raw e com URL assinada, sem alterar as imagens globais.
from .storage import SignedRawMediaCloudinaryStorage

class CategoriaDocumento(models.Model):
    nome = models.CharField("Nome da Categoria", max_length=100)
    
    class Meta:
        verbose_name = "Categoria de Documento"
        verbose_name_plural = "Categorias de Documentos"
    
    def __str__(self):
        return self.nome

class DocumentoRestrito(models.Model):
    titulo = models.CharField("Título do Documento", max_length=200)
    descricao = models.TextField("Descrição/Observação", blank=True, null=True)
    
    # A MÁGICA AQUI: O parâmetro 'storage' força o Cloudinary a aceitar PDFs, DOCs, etc., sem corromper.
    # O max_length=500 garante que nomes de arquivos longos não quebrem o banco.
    arquivo = models.FileField(
        upload_to='intranet_docs/', 
        storage=SignedRawMediaCloudinaryStorage(),
        blank=True, 
        null=True, 
        max_length=500
    )
    
    link = models.URLField("Link Externo (Google Drive, etc)", blank=True, null=True)
    
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
        
    def save(self, *args, **kwargs):
        # Truncamento de segurança: Se o título for maior que 200, corta ele antes de salvar
        if self.titulo and len(self.titulo) > 200:
            self.titulo = self.titulo[:197] + "..."
        super().save(*args, **kwargs)