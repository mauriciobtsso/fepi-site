# blogs/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # A URL espera receber o subdominio, ex: /blogs/dije/
    path('<str:subdominio>/', views.home_blog, name='home_blog'),
    
    # A URL para ler um post, ex: /blogs/dije/nossa-primeira-postagem/
    path('<str:subdominio>/<slug:slug>/', views.ler_post, name='ler_post'),
]