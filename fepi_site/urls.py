from django.contrib import admin
from django.urls import path, include, re_path # <--- include é essencial aqui
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve 

from django.contrib.auth import views as auth_views

# Views diretas (Mantive as que não têm urls.py próprios ainda)
from recursos.views import links_uteis, downloads
from doacoes.views import doacoes_view
from core.views import home, institucional, fale_conosco, privacidade
from livraria.views import detalhe_livro, livraria_completa
from centros.views import lista_centros
from programacao.views import atividades, doutrinarias, calendario, lista_cursos, detalhe_curso
from intranet.views import area_federado

# NOTA: Removi a importação de 'noticias.views' porque agora usamos o include

urlpatterns = [
    path('admin/', admin.site.urls),
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
    path('livro/<int:livro_id>/', detalhe_livro, name='detalhe_livro'),
    
    # --- MUDANÇA AQUI: Incluir as URLs da app Noticias ---
    # Isto faz o Django ler o arquivo noticias/urls.py que criaste
    path('noticias/', include('noticias.urls')), # O prefixo será /noticias/...
    
    # O path antigo foi removido daqui para não dar conflito

    path('links-uteis/', links_uteis, name='links_uteis'),
    path('downloads/', downloads, name='downloads'),
    path('doar/', doacoes_view, name='doacoes_view'),
    
    # Inclusão do CKEditor (Importante para o upload de imagens funcionar)
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# --- CONFIGURAÇÃO PARA SERVIR ARQUIVOS DE MÍDIA NO RAILWAY ---
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)