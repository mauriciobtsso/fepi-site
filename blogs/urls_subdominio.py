from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from . import views

urlpatterns = [
    # O pacote django-hosts já injeta a variável "subdominio" invisivelmente aqui!
    path('', views.home_blog, name='home_blog'),
    path('<slug:slug>/', views.ler_post, name='ler_post'),
]

# Proteção para garantir que as imagens carreguem se acessar direto pelo subdomínio localmente
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]