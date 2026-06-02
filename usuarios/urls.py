from django.urls import path
from . import views

urlpatterns = [
    path('seja-membro/', views.seja_membro, name='seja_membro'),
    path('minha-conta/', views.minha_conta, name='minha_conta'), # <- Rota do Membro Comum
]