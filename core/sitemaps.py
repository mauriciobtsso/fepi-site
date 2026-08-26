from django.contrib.sitemaps import Sitemap
from django.urls import reverse

# 🔴 CORREÇÃO DA CORREÇÃO: 
# A Notícia foi para 'noticias', mas o EventoAgenda continua no 'core'!
from noticias.models import Noticia
from core.models import EventoAgenda
from livraria.models import Livro

class StaticViewSitemap(Sitemap):
    """Páginas estáticas (Home, Institucional, Fale Conosco, etc)"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'home', 
            'institucional', 
            'fale_conosco', 
            'livraria',       # Era livraria_publica
            'lista_centros', 
            'doacoes_view',   # Era doacoes
            'downloads',      # Era recursos_publicos
            'links_uteis',    
            'atividades',     # Era agenda_publica
            'doutrinarias',   
            'calendario',     
            'privacidade'     
        ]

    def location(self, item):
        return reverse(item)

class NoticiaSitemap(Sitemap):
    """Mapeia todas as notícias"""
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Noticia.objects.all().order_by('-data_publicacao')

    def lastmod(self, obj):
        return obj.data_publicacao

    def location(self, obj):
        try:
            return reverse('detalhe_noticia', args=[obj.slug])
        except:
            return f"/noticias/{obj.slug}/"

class LivroSitemap(Sitemap):
    """Mapeia todos os livros"""
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Livro.objects.filter(ativo_na_vitrine=True)

    def location(self, obj):
        return reverse('detalhe_livro', args=[obj.slug])

class EventoSitemap(Sitemap):
    """Mapeia eventos futuros"""
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        from django.utils import timezone
        return EventoAgenda.objects.filter(data_inicio__gte=timezone.now())
    
    # Se os eventos não tiverem página própria (forem só modal),
    # retornamos a página de cursos como referência
    def location(self, obj):
        return reverse('lista_cursos')