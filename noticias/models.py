from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.utils.text import slugify # <--- Importante para criar o slug

class Noticia(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    
    # NOVO CAMPO SLUG
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug / Link Amigável")
    
    autor = models.CharField(max_length=100, verbose_name="Autor", default="FEPI")
    data_publicacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Publicação")
    conteudo = RichTextField(verbose_name="Conteúdo da Notícia")
    imagem = models.ImageField(upload_to='noticias/', blank=True, null=True, verbose_name="Imagem de Capa")
    
    def save(self, *args, **kwargs):
        # Se o slug estiver vazio, cria um a partir do título
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"
        ordering = ['-data_publicacao']