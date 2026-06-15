from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.utils.text import slugify
from django_editorjs_fields import EditorJsJSONField
import json # 🔴 IMPORTANTE: Biblioteca que transforma texto em blocos

class Noticia(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    autor = models.CharField(max_length=100, verbose_name="Autor", default="FEPI")
    data_publicacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Publicação")
    
    # NOVO CAMPO RESUMO (Texto simples, sem HTML, para o card)
    resumo = models.TextField(max_length=500, verbose_name="Resumo (Aparece na lista)", blank=True, help_text="Um texto curto para chamar a atenção.")
    
    conteudo = RichTextField(verbose_name="Conteúdo Antigo (Não preencher em novas notícias)", blank=True, null=True)
    
    conteudo_blocos = EditorJsJSONField(
        verbose_name='Conteúdo da Notícia (Editor Moderno)',
        plugins=[
            "@editorjs/image",
            "@editorjs/header",
            "@editorjs/list",
            "@editorjs/quote",
            "@editorjs/embed",
        ],
        blank=True, null=True
    )
    
    imagem = models.ImageField(upload_to='noticias/', blank=True, null=True, verbose_name="Imagem de Capa")
    
    # 🔴 NOVA FUNÇÃO VITAL: Traduz o texto guardado no banco para uma lista real de blocos
    def get_blocos_dit(self):
        if self.conteudo_blocos and str(self.conteudo_blocos).strip() not in ['null', '', '{}']:
            try:
                # Se o banco de dados já entregou em dicionário
                if isinstance(self.conteudo_blocos, dict):
                    return self.conteudo_blocos
                # Se entregou em texto, converte
                return json.loads(self.conteudo_blocos)
            except Exception:
                return None
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"
        ordering = ['-data_publicacao']