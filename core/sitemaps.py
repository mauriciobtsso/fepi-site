from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from core.models import Noticia, EventoAgenda
from livraria.models import Livro

class StaticViewSitemap(Sitemap):
    """Páginas estáticas (Home, Institucional, Fale Conosco, etc)"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        # AQUI ESTAVA O ERRO: Usei nomes que não existiam no urls.py.
        # Agora estou usando os nomes exatos do seu arquivo urls.py:
        return [
            'home', 
            'institucional', 
            'fale_conosco', 
            'livraria',       # Era livraria_publica
            'lista_centros', 
            'doacoes_view',   # Era doacoes
            'downloads',      # Era recursos_publicos
            'links_uteis',    # Adicionado
            'atividades',     # Era agenda_publica
            'doutrinarias',   # Adicionado
            'calendario',     # Adicionado
            'privacidade'     # Adicionado
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
        # Tenta reverter a URL de detalhe. O nome 'detalhe_noticia' deve existir em noticias/urls.py
        # Se der erro aqui, é porque o nome da rota na app noticias é outro.
        try:
            return reverse('detalhe_noticia', args=[obj.slug])
        except:
            return f"/noticias/{obj.slug}/"

class LivroSitemap(Sitemap):
    """Mapeia todos os livros"""
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Livro.objects.all()

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