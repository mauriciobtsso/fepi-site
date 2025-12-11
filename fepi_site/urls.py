from django.contrib import admin
from django.urls import path, include # Importante: include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views # Views prontas de login

from recursos.views import links_uteis, downloads
from doacoes.views import doacoes_view
from core.views import home, institucional, fale_conosco, privacidade
from livraria.views import detalhe_livro, livraria_completa
from noticias.views import detalhe_noticia, lista_noticias
from centros.views import lista_centros
from programacao.views import atividades, doutrinarias, calendario, lista_cursos, detalhe_curso
from intranet.views import area_federado # <--- Nova view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    
    # --- SISTEMA DE LOGIN E INTRANET ---
    # Rota de Login (usa template padrão registration/login.html)
    path('login/', auth_views.LoginView.as_view(), name='login'),
    # Rota de Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Área Protegida
    path('area-federado/', area_federado, name='area_federado'),

    # Institucional
    path('institucional/', institucional, name='institucional'),
    path('privacidade/', privacidade, name='privacidade'),
    
    # Programação
    path('atividades/', atividades, name='atividades'),
    path('doutrinarias/', doutrinarias, name='doutrinarias'),
    path('calendario/', calendario, name='calendario'),
    path('cursos/', lista_cursos, name='lista_cursos'),
    path('curso/<int:curso_id>/', detalhe_curso, name='detalhe_curso'),
    
    # Outros
    path('fale-conosco/', fale_conosco, name='fale_conosco'),
    path('livraria/', livraria_completa, name='livraria'),
    path('centros/', lista_centros, name='lista_centros'),
    path('livro/<int:livro_id>/', detalhe_livro, name='detalhe_livro'),
    path('noticia/<int:noticia_id>/', detalhe_noticia, name='detalhe_noticia'),
    path('noticias/', lista_noticias, name='lista_noticias'),
    path('links-uteis/', links_uteis, name='links_uteis'),
    path('downloads/', downloads, name='downloads'),
    path('doar/', doacoes_view, name='doacoes_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)