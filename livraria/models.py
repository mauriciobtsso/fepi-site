from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.contrib.auth.models import User

# 1. Tabela de Configuração da Livraria (Logo e Redes)
class LivrariaConfig(models.Model):
    logo = models.ImageField(upload_to='livraria_config/', blank=True, null=True, verbose_name="Logo da Livraria (Branding)")
    
    # NOVOS CAMPOS
    whatsapp = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="WhatsApp de Vendas",
        help_text="Digite apenas números, com DDD. Ex: 5535999887766"
    )
    
    instagram_url = models.URLField(
        blank=True, 
        null=True, 
        verbose_name="Link do Perfil do Instagram",
        help_text="Ex: https://www.instagram.com/livrariaramirogama"
    )
    
    instagram_widget_code = models.TextField(blank=True, verbose_name="Código do Widget do Instagram (SnapWidget)")
    
    # Singleton: Garante que só existe 1 registro
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
    codigo = models.CharField(max_length=50, verbose_name="Código / ISBN", default="0000", db_index=True)
    titulo = models.CharField(max_length=255, verbose_name="Título")
    
    # NOVO: Slug para link amigável (ex: /livro/nosso-lar)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, verbose_name="Link Amigável")
    
    autor = models.CharField(max_length=100, verbose_name="Autor")
    
    # Ligação à Categoria
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria")
    
    # Campo alterado para permitir formatação (RichText)
    descricao = RichTextField(blank=True, null=True, verbose_name="Descrição")
    
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço")
    
    # Dados operacionais sincronizados pela planilha de estoque
    quantidade_estoque = models.IntegerField(default=0, verbose_name="Quantidade em estoque")
    ultima_sincronizacao = models.DateTimeField(blank=True, null=True, verbose_name="Última sincronização")
    
    # Controles independentes da vitrine e da disponibilidade
    destaque_home = models.BooleanField(default=False, verbose_name="Destaque Rotativo na Home")
    ativo_na_vitrine = models.BooleanField(default=True, verbose_name="Ativo na vitrine")
    disponivel = models.BooleanField(default=False, verbose_name="Disponível para venda")
    capa = models.ImageField(upload_to='capas/', blank=True, null=True, verbose_name="Capa do Livro")
    
    def save(self, *args, **kwargs):
        # Garante que o slug existe antes de salvar
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

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


class ProdutoLivraria(models.Model):
    codigo_barras = models.CharField(max_length=50, unique=True, db_index=True)
    descricao = models.CharField(max_length=255)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_estoque = models.IntegerField(default=0)
    editora = models.CharField(max_length=100, blank=True, null=True)
    
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produto da Livraria'
        verbose_name_plural = 'Produtos da Livraria'

    def __str__(self):
        return f"{self.codigo_barras} - {self.descricao}"

class HistoricoUploadProdutos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_upload = models.DateTimeField(auto_now_add=True)
    sucesso = models.BooleanField(default=True)
    mensagem = models.TextField(blank=True) # Ex: "Upload realizado com sucesso" ou erro do Pandas

    class Meta:
        verbose_name = 'Histórico de Upload'
        verbose_name_plural = 'Histórico de Uploads'
        ordering = ['-data_upload'] # Ordena sempre do mais recente para o mais antigo

    def __str__(self):
        status = "Sucesso" if self.sucesso else "Erro"
        return f"{self.data_upload.strftime('%d/%m/%Y %H:%M')} - {status}"


