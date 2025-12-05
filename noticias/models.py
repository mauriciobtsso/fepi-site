from django.db import models

class Noticia(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    resumo = models.TextField(blank=True, verbose_name="Resumo (para lista)")
    conteudo = models.TextField()
    
    # Campo para quem publicou
    autor = models.CharField(max_length=100, default="FEPI", verbose_name="Autor da Publicação")
    
    imagem = models.ImageField(upload_to='noticias_capas/', blank=True, null=True)
    data_publicacao = models.DateTimeField(auto_now_add=True)
    
    # CAMPO QUE ESTAVA A FALTAR E CAUSAVA O ERRO DE ADMIN
    foi_publicada = models.BooleanField(default=True, verbose_name="Publicada no Site") 

    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"
        ordering = ['-data_publicacao']