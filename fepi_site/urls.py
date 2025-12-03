from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Imports das Views (ATENÇÃO: importamos 'institucional' aqui)
from core.views import home, institucional
from livraria.views import detalhe_livro
from noticias.views import detalhe_noticia

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    
    # Rota do Institucional (que estava dando erro)
    path('institucional/', institucional, name='institucional'),
    
    # Rotas de Detalhes
    path('livro/<int:livro_id>/', detalhe_livro, name='detalhe_livro'),
    path('noticia/<int:noticia_id>/', detalhe_noticia, name='detalhe_noticia'),
]

# Configuração para imagens e estáticos funcionarem
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)