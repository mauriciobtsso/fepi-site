from django.db import models

class SecaoLink(models.Model):
    """ Define a categoria dos links (ex: Arte, Federativas) """
    nome = models.CharField(max_length=100, verbose_name="Nome da Secção/Grupo")
    icone_fa = models.CharField(max_length=30, default="fa-solid fa-link", verbose_name="Ícone FontAwesome")
    ordem = models.IntegerField(default=1, verbose_name="Ordem de Exibição")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Secção de Link"
        verbose_name_plural = "Secções de Links"
        ordering = ['ordem']

class LinkItem(models.Model):
    """ Define um item de link ou download """
    secao = models.ForeignKey(SecaoLink, on_delete=models.CASCADE, verbose_name="Secção")
    titulo = models.CharField(max_length=200)
    url = models.URLField(verbose_name="Endereço URL (http://...)")
    descricao = models.TextField(blank=True, verbose_name="Descrição (Opcional)")
    is_download = models.BooleanField(default=False, verbose_name="É um Download (Mostrar botão)?")
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name = "Item de Link/Download"
        verbose_name_plural = "Itens de Links/Downloads"
        ordering = ['titulo']