from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='painel_home'),
    path('noticias/nova/', views.criar_noticia, name='criar_noticia'),

    # --- NOVAS ROTAS ---
    path('noticias/', views.listar_noticias, name='listar_noticias'),
    path('noticias/editar/<int:noticia_id>/', views.editar_noticia, name='editar_noticia'),
    path('noticias/deletar/<int:noticia_id>/', views.deletar_noticia, name='deletar_noticia'),
    path('popup/', views.gerenciar_popup, name='gerenciar_popup'),

# Documentos
    path('documentos/', views.listar_documentos, name='listar_documentos'),
    path('documentos/novo/', views.criar_documento, name='criar_documento'),
    path('documentos/editar/<int:id>/', views.editar_documento, name='editar_documento'),
    path('documentos/excluir/<int:id>/', views.excluir_documento, name='excluir_documento'),
    
    # Categorias
    path('documentos/categorias/', views.listar_categorias_doc, name='listar_categorias_doc'),
    path('documentos/categorias/excluir/<int:id>/', views.excluir_categoria_doc, name='excluir_categoria_doc'),

]