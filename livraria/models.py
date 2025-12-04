from django.db import models

# 1. Nova Tabela de Categorias (Dinâmica)
class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']

# 2. Modelo do Livro (Atualizado)
class Livro(models.Model):
    # O campo 'codigo' continua igual
    codigo = models.CharField(max_length=20, verbose_name="Código / ISBN", default="0000")
    
    titulo = models.CharField(max_length=100, verbose_name="Título")
    autor = models.CharField(max_length=100, verbose_name="Autor")
    
    # AGORA SIM: O campo está ativo e é uma Chave Estrangeira (ForeignKey)
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL, # Se apagar a categoria, o livro não é apagado
        null=True, 
        blank=True, 
        verbose_name="Categoria"
    )
    
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    preco = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Preço")
    disponivel = models.BooleanField(default=True, verbose_name="Disponível em Estoque")
    capa = models.ImageField(upload_to='capas/', blank=True, null=True, verbose_name="Capa do Livro")
    
    def __str__(self):
        return f"[{self.codigo}] {self.titulo}"
        
    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"
        ordering = ['titulo']