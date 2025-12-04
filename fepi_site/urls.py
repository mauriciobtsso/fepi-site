from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# 1. Imports do Core (Home, Institucional, Fale Conosco, Livraria Completa)
from core.views import home, institucional, fale_conosco, livraria_completa

# 2. Imports da Livraria (Detalhes do livro individual)
from livraria.views import detalhe_livro

# 3. Imports de Notícias (Detalhe da notícia)
from noticias.views import detalhe_noticia

# 4. Imports de Centros
from centros.views import lista_centros

# 5. Imports de Programação (Atividades, Doutrinárias, Calendário) <--- O QUE FALTAVA
from programacao.views import atividades, doutrinarias, calendario

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    
    # Institucional
    path('institucional/', institucional, name='institucional'),
    
    # Programação e Atividades (Novas Rotas)
    path('atividades/', atividades, name='atividades'),
    path('doutrinarias/', doutrinarias, name='doutrinarias'),
    path('calendario/', calendario, name='calendario'),
    
    # Contato e Livraria Geral
    path('fale-conosco/', fale_conosco, name='fale_conosco'),
    path('livraria/', livraria_completa, name='livraria'),
    
    # Centros Espíritas
    path('centros/', lista_centros, name='lista_centros'),
    
    # Rotas de Detalhes (Páginas internas)
    path('livro/<int:livro_id>/', detalhe_livro, name='detalhe_livro'),
    path('noticia/<int:noticia_id>/', detalhe_noticia, name='detalhe_noticia'),
]

# Configuração para imagens e estáticos funcionarem no modo Debug
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)