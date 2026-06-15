import json
from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.utils.text import slugify
from django_editorjs_fields import EditorJsJSONField

class Noticia(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    autor = models.CharField(max_length=100, verbose_name="Autor", default="FEPI")
    data_publicacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Publicação")
    
    resumo = models.TextField(max_length=500, verbose_name="Resumo (Aparece na lista)", blank=True, help_text="Um texto curto para chamar a atenção.")
    
    conteudo = RichTextField(verbose_name="Conteúdo Antigo (Não preencher em novas notícias)", blank=True, null=True)
    
    # 🔴 ATUALIZADO: Autorizando o EditorJS a processar vídeos do YouTube, Insta, etc.
    conteudo_blocos = EditorJsJSONField(
        verbose_name='Conteúdo da Notícia (Editor Moderno)',
        plugins=[
            "@editorjs/image",
            "@editorjs/header",
            "@editorjs/list",
            "@editorjs/quote",
            "@editorjs/embed",
        ],
        tools={
            "Embed": {
                "class": "Embed",
                "config": {
                    "services": {
                        "youtube": True,
                        "vimeo": True,
                        "instagram": True,
                        "facebook": True
                    }
                }
            }
        },
        blank=True, null=True
    )
    
    imagem = models.ImageField(upload_to='noticias/', blank=True, null=True, verbose_name="Imagem de Capa")
    
    def get_blocos_list(self):
        raw_data = self.conteudo_blocos
        
        if not raw_data or raw_data == 'null' or raw_data == '{}':
            return []
            
        data = raw_data
        
        # Converte de String JSON para Dicionário Python
        while isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                break
                
        # Extrai a lista de blocos
        blocos_originais = []
        if isinstance(data, dict):
            blocos_originais = data.get('blocks', [])
        elif isinstance(data, list):
            blocos_originais = data
            
        # Filtro que limpa nomes estranhos
        blocos_limpos = []
        for b in blocos_originais:
            if isinstance(b, dict) and 'type' in b:
                tipo_limpo = str(b['type']).lower().replace('@editorjs/', '').strip()
                b['type'] = tipo_limpo
                blocos_limpos.append(b)
                
        return blocos_limpos

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