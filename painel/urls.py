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
]