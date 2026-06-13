from django.urls import path
from . import views

urlpatterns = [
    path('minha-conta/', views.minha_conta, name='minha_conta'), # <- Rota do Membro Comum
]