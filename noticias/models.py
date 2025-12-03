from django.db import models

class Noticia(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    resumo = models.TextField(verbose_name="Resumo (para a capa)", help_text="Um texto curto para chamar a atenção na página inicial.")
    conteudo = models.TextField(verbose_name="Conteúdo Completo")
    imagem = models.ImageField(upload_to='noticias/', blank=True, null=True, verbose_name="Imagem de Destaque")
    data_publicacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Publicação")
    
    def __str__(self):
        return self.titulo
        
    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"
        ordering = ['-data_publicacao'] # Garante que a mais recente aparece primeiro