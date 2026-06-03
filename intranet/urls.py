from django.urls import path
from . import views

urlpatterns = [
    path('', views.area_federado, name='area_federado'),
    path('artigos/', views.meus_artigos, name='meus_artigos'),
    path('artigos/novo/', views.redigir_artigo, name='novo_artigo'),
    path('artigos/editar/<int:pk>/', views.redigir_artigo, name='editar_artigo'),
    
    # --- PORTAL DO VOLUNTÁRIO ---
    path('voluntariado/', views.voluntariado_intro, name='voluntariado_intro'),
    path('voluntariado/cadastro/', views.voluntariado_cadastro, name='voluntariado_cadastro'),
]