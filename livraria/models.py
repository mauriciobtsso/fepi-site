from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField

# 1. Tabela de Configuração da Livraria (Logo e Redes)
class LivrariaConfig(models.Model):
    logo = models.ImageField(upload_to='livraria_config/', blank=True, null=True, verbose_name="Logo da Livraria (Branding)")
    instagram_widget_code = models.TextField(blank=True, verbose_name="Código do Widget do Instagram (SnapWidget)")
    
    # Singleton: Garante que só existe 1 registo
    def save(self, *args, **kwargs):
        if not self.pk and LivrariaConfig.objects.exists():
            return
        super(LivrariaConfig, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Configuração da Livraria"
        verbose_name_plural = "Configuração da Livraria"

    def __str__(self):
        return "Configuração Ramiro Gama"


# 2. Tabela de Categorias
class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']


# 3. Modelo do Livro
class Livro(models.Model):
    codigo = models.CharField(max_length=20, verbose_name="Código / ISBN", default="0000")
    titulo = models.CharField(max_length=100, verbose_name="Título")
    autor = models.CharField(max_length=100, verbose_name="Autor")
    
    # Ligação à Categoria
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria")
    
    # Campo alterado para permitir formatação
    descricao = RichTextField(blank=True, null=True, verbose_name="Descrição")
    
    preco = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Preço")
    
    # Destaque na Home
    destaque_home = models.BooleanField(default=False, verbose_name="Destaque Rotativo na Home")
    
    disponivel = models.BooleanField(default=True, verbose_name="Disponível em Estoque")
    capa = models.ImageField(upload_to='capas/', blank=True, null=True, verbose_name="Capa do Livro")
    
    def __str__(self):
        return f"[{self.codigo}] {self.titulo}"
        
    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"
        ordering = ['titulo']


# SINAL para criar o objeto de configuração automaticamente se não existir
@receiver(post_save, sender=LivrariaConfig)
def ensure_singleton_exists(sender, **kwargs):
    if not LivrariaConfig.objects.exists():
        LivrariaConfig.objects.create()