# blogs/models.py
from django.db import models
from django.contrib.auth.models import User
from django_editorjs_fields import EditorJsJSONField

class BlogDepartamento(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Departamento", help_text="Ex: Departamento de Infância e Juventude (DIJE)")
    subdominio = models.CharField(max_length=50, unique=True, help_text="Ex: 'dije' (o link ficará dije.fepiaui.org.br)")
    cor_primaria = models.CharField(max_length=7, default="#008080", help_text="Cor principal em HEX (para personalizar o template)")
    logo = models.ImageField(upload_to='blogs/logos/', blank=True, null=True)
    descricao = models.TextField(blank=True, help_text="Pequeno texto sobre o departamento")
    
    # --- CAMPOS PARA O INSTAGRAM ---
    instagram_url = models.URLField(blank=True, null=True, verbose_name="URL do Instagram", help_text="Ex: https://instagram.com/dije_fepi")
    instagram_widget_code = models.TextField(blank=True, null=True, verbose_name="Código do Widget do Instagram", help_text="Cole aqui o código embed/iframe obtido em ferramentas gratuitas")
    
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Blog de Departamento"
        verbose_name_plural = "Blogs de Departamentos"

    def __str__(self):
        return f"{self.nome} ({self.subdominio}.fepiaui.org.br)"


class CategoriaBlog(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Nome da Categoria")
    slug = models.SlugField(max_length=60, unique=True)
    cor = models.CharField(max_length=7, default="#7f8c8d", help_text="Cor da tag em HEX (ex: #3498db)")

    class Meta:
        verbose_name = "Categoria do Blog"
        verbose_name_plural = "Categorias dos Blogs"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class PostBlog(models.Model):
    departamento = models.ForeignKey(BlogDepartamento, on_delete=models.CASCADE, related_name='posts')
    categoria = models.ForeignKey(CategoriaBlog, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', verbose_name="Categoria / Tag")
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    resumo = models.TextField(max_length=500, blank=True, help_text="Aparece na lista de postagens do blog")
    
    # Declaramos o campo sem a lista de plugins aqui para evitar o erro de inicialização.
    # A configuração do EditorJS deve ser feita via widget no forms.py ou settings.py
    conteudo = EditorJsJSONField(
        verbose_name="Conteúdo do Artigo"
    )
    
    imagem_capa = models.ImageField(upload_to='blogs/capas/', blank=True, null=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nome_autor_externo = models.CharField(max_length=100, blank=True, help_text="Preencher caso o autor não tenha conta no sistema")
    data_publicacao = models.DateTimeField()
    publicado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Postagem do Blog"
        verbose_name_plural = "Postagens dos Blogs"
        ordering = ['-data_publicacao']

    def __str__(self):
        return f"[{self.departamento.subdominio}] {self.titulo}"