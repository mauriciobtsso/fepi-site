from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.static import serve 
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from core import views
import os
from core.forms import CustomPasswordResetForm

# --- IMPORT NECESSÁRIO PARA O ROBOTS.TXT ---
from django.views.generic.base import TemplateView

# Views diretas
from recursos.views import links_uteis, downloads
from doacoes.views import doacoes_view
from core.views import home, institucional, fale_conosco, privacidade
from usuarios import views as usuarios_views

# --- IMPORTS DOS SITEMAPS ---
from core.sitemaps import StaticViewSitemap, NoticiaSitemap, LivroSitemap, EventoSitemap

from livraria.views import detalhe_livro, livraria_completa
from centros.views import lista_centros, api_centros_proximidade
from programacao.views import atividades, doutrinarias, calendario, lista_cursos, detalhe_curso

# --- DEFINIÇÃO DO DICIONÁRIO SITEMAPS ---
sitemaps = {
    'estaticas': StaticViewSitemap,
    'noticias': NoticiaSitemap,
    'livros': LivroSitemap,
    'eventos': EventoSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('painel/', include('painel.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', home, name='home'),
    path('editorjs/', include('django_editorjs_fields.urls')),
    
    # --- SISTEMA DE LOGIN E INTRANET ---
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Agora a área do federado e os artigos do colunista são controlados pelas rotas da intranet
    path('area-federado/', include('intranet.urls')),

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
    path('api/centros-proximidade/', api_centros_proximidade, name='api_centros_proximidade'),
    path('painel/voluntarios/', include('voluntarios.urls')),
    
    # Livraria Detalhe
    path('livraria/<slug:slug>/', detalhe_livro, name='detalhe_livro'),
    
    # Notícias
    path('noticias/', include('noticias.urls')),
    path('coluna/<slug:slug>/', views.detalhe_coluna, name='detalhe_coluna'),

    path('links-uteis/', links_uteis, name='links_uteis'),
    path('downloads/', downloads, name='downloads'),
    path('doar/', doacoes_view, name='doacoes_view'),
    path('seja-membro/', usuarios_views.seja_membro, name='seja_membro'),
    path('usuarios/', include('usuarios.urls')),

    path('vozes-da-fepi/', views.listar_colunas_publicas, name='colunas'),
    path('vozes-da-fepi/artigo/<slug:slug>/', views.detalhe_coluna, name='detalhe_coluna'),
    
    # --- SEO (Google) ---
    # 1. Sitemap.xml 
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # 2. Robots.txt 
    path("robots.txt", TemplateView.as_view(template_name="core/robots.txt", content_type="text/plain")),

    # --- RECUPERAÇÃO DE SENHA ---
    path('recuperar-senha/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             form_class=CustomPasswordResetForm,
             html_email_template_name='registration/password_reset_email.html', # <-- FALTAVA ISSO
             subject_template_name='registration/password_reset_subject.txt'    # <-- FALTAVA ISSO
         ), 
         name='password_reset'),
         
    path('recuperar-senha/enviado/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),
         
    path('recuperar-senha/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
         
    path('recuperar-senha/concluido/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),

]

# --- CONFIGURAÇÃO PARA SERVIR ARQUIVOS DE MÍDIA NO RAILWAY ---
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

def debug_static(request):
    import subprocess
    result = subprocess.run(
        ['python', 'manage.py', 'collectstatic', '--noinput', '--verbosity=2'],
        capture_output=True, text=True, cwd='/app'
    )
    return JsonResponse({
        'static_root': str(settings.STATIC_ROOT),
        'staticfiles_dirs': [str(d) for d in settings.STATICFILES_DIRS],
        'stdout': result.stdout[-3000:],
        'stderr': result.stderr[-3000:],
    })

urlpatterns += [path('debug-static/', debug_static)]