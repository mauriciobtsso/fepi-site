from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.static import serve 
from django.contrib.auth import views as auth_views

# --- IMPORT NECESSÁRIO PARA O ROBOTS.TXT (FALTAVA ESSE) ---
from django.views.generic.base import TemplateView

# Views diretas
from recursos.views import links_uteis, downloads
from doacoes.views import doacoes_view
from core.views import home, institucional, fale_conosco, privacidade

# --- IMPORTS DOS SITEMAPS (ADICIONEI EventoSitemap) ---
from core.sitemaps import StaticViewSitemap, NoticiaSitemap, LivroSitemap, EventoSitemap

from livraria.views import detalhe_livro, livraria_completa
from centros.views import lista_centros
from programacao.views import atividades, doutrinarias, calendario, lista_cursos, detalhe_curso
from intranet.views import area_federado

# --- DEFINIÇÃO DO DICIONÁRIO SITEMAPS (O ERRO ERA A FALTA DISSO) ---
sitemaps = {
    'estaticas': StaticViewSitemap,
    'noticias': NoticiaSitemap,
    'livros': LivroSitemap,
    'eventos': EventoSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('painel/', include('painel.urls')),
    path('', home, name='home'),
    
    # --- SISTEMA DE LOGIN E INTRANET ---
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('area-federado/', area_federado, name='area_federado'),

    # Institucional
    path('institucional/', institucional, name='institucional'),
    path('privacidade/', privacidade, name='privacidade'),
    
    # Programação
    path('atividades/', atividades, name='atividades'),
    path('doutrinarias/', doutrinarias, name='doutrinarias'),
    path('calendario/', calendario, name='calendario'),
    path('cursos/', lista_cursos, name='lista_cursos'),
    path('curso/<slug:slug>/', detalhe_curso, name='detalhe_curso'),
    
    # Outros
    path('fale-conosco/', fale_conosco, name='fale_conosco'),
    path('livraria/', livraria_completa, name='livraria'),
    path('centros/', lista_centros, name='lista_centros'),
    
    # Livraria Detalhe
    path('livraria/<slug:slug>/', detalhe_livro, name='detalhe_livro'),
    
    # Notícias
    path('noticias/', include('noticias.urls')),

    path('links-uteis/', links_uteis, name='links_uteis'),
    path('downloads/', downloads, name='downloads'),
    path('doar/', doacoes_view, name='doacoes_view'),
    
    # CKEditor
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # --- SEO (Google) ---
    # 1. Sitemap.xml (Agora vai funcionar pois 'sitemaps' foi definido acima)
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # 2. Robots.txt (Agora funciona pois importamos TemplateView)
    path("robots.txt", TemplateView.as_view(template_name="core/robots.txt", content_type="text/plain")),
]

# --- CONFIGURAÇÃO PARA SERVIR ARQUIVOS DE MÍDIA NO RAILWAY ---
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)