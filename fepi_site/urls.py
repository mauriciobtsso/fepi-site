from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Imports das Views
from core.views import home
from livraria.views import detalhe_livro  # <--- IMPORTANTE: Importar a nova view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    
    # Rota nova: Quando alguém acessar "livro/1", o Django manda o número 1 para a view
    path('livro/<int:livro_id>/', detalhe_livro, name='detalhe_livro'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Adiciona também a rota para os estáticos (Logo/CSS) funcionarem sempre bem
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)