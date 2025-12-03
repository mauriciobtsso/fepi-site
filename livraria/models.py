from django.db import models

class Livro(models.Model):
    titulo = models.CharField(max_length=100, verbose_name="Título")
    autor = models.CharField(max_length=100, verbose_name="Autor")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    preco = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Preço")
    disponivel = models.BooleanField(default=True, verbose_name="Disponível em Estoque")
    
    # Esta função diz ao Django para mostrar o nome do livro e não "Objeto Livro 1"
    def __str__(self):
        return self.titulo
        
    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"