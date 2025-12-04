from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# 1. Imports do Core (Home, Institucional, Fale Conosco)
# REMOVIDO: livraria_completa daqui
from core.views import home, institucional, fale_conosco

# 2. Imports da Livraria (Detalhes E Lista Completa)
# ADICIONADO: livraria_completa aqui
from livraria.views import detalhe_livro, livraria_completa

# 3. Imports de Notícias
from noticias.views import detalhe_noticia, lista_noticias

# 4. Imports de Centros
from centros.views import lista_centros

# 5. Imports de Programação
from programacao.views import atividades, doutrinarias, calendario, lista_cursos, detalhe_curso

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    
    # Institucional
    path('institucional/', institucional, name='institucional'),
    
    # Programação e Atividades
    path('atividades/', atividades, name='atividades'),
    path('doutrinarias/', doutrinarias, name='doutrinarias'),
    path('calendario/', calendario, name='calendario'),
    path('cursos/', lista_cursos, name='lista_cursos'),
    path('curso/<int:curso_id>/', detalhe_curso, name='detalhe_curso'),
    
    # Contato e Livraria Geral
    path('fale-conosco/', fale_conosco, name='fale_conosco'),
    path('livraria/', livraria_completa, name='livraria'),
    
    # Centros Espíritas
    path('centros/', lista_centros, name='lista_centros'),
    
    # Rotas de Detalhes e Listas
    path('livro/<int:livro_id>/', detalhe_livro, name='detalhe_livro'),
    path('noticia/<int:noticia_id>/', detalhe_noticia, name='detalhe_noticia'),
    path('noticias/', lista_noticias, name='lista_noticias'),
]

# Configuração para imagens e estáticos funcionarem no modo Debug
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)