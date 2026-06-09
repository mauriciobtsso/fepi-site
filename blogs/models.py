from django.db import models
from django.contrib.auth.models import User

class BlogDepartamento(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Departamento", help_text="Ex: Departamento de Infância e Juventude (DIJE)")
    subdominio = models.CharField(max_length=50, unique=True, help_text="Ex: 'dije' (o link ficará dije.fepi.org.br)")
    cor_primaria = models.CharField(max_length=7, default="#0056b3", help_text="Cor principal em HEX (para personalizar o template)")
    logo = models.ImageField(upload_to='blogs/logos/', blank=True, null=True)
    descricao = models.TextField(blank=True, help_text="Pequeno texto sobre o departamento")
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Blog de Departamento"
        verbose_name_plural = "Blogs de Departamentos"

    def __str__(self):
        return f"{self.nome} ({self.subdominio}.fepi.org.br)"

class PostBlog(models.Model):
    departamento = models.ForeignKey(BlogDepartamento, on_delete=models.CASCADE, related_name='posts')
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    resumo = models.TextField(max_length=500, blank=True, help_text="Aparece na lista de postagens do blog")
    conteudo = models.TextField(help_text="Conteúdo completo (usará o CKEditor no painel)")
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