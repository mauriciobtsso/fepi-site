# intranet/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.area_federado, name='area_federado'),
    path('artigos/', views.meus_artigos, name='meus_artigos'),
    path('artigos/novo/', views.redigir_artigo, name='novo_artigo'),
    path('artigos/editar/<int:pk>/', views.redigir_artigo, name='editar_artigo'),
    
    # --- PORTAL DO VOLUNTÁRIO (AUTOATENDIMENTO) ---
    path('voluntariado/', views.voluntariado_intro, name='voluntariado_intro'),
    path('voluntariado/cadastro/', views.voluntariado_cadastro, name='voluntariado_cadastro'),
    path('voluntariado/painel/', views.voluntariado_painel, name='voluntariado_painel'),
    path('voluntariado/termo/imprimir/', views.voluntariado_imprimir_termo, name='voluntariado_imprimir_termo'),
    
    # --- 🔴 SALA DE REDAÇÃO DEPARTAMENTAL (NOVO) ---
    path('meu-blog/', views.meu_blog_hub, name='meu_blog_hub'),
    path('meu-blog/novo/', views.redigir_post_blog, name='novo_post_blog_intranet'),
    path('meu-blog/editar/<int:id>/', views.redigir_post_blog, name='editar_post_blog_intranet'),
    path('meu-blog/excluir/<int:id>/', views.excluir_post_blog, name='excluir_post_blog_intranet'),
]