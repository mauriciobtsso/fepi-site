from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_noticias, name='lista_noticias'),
    # MUDANÇA AQUI: de <int:noticia_id> para <slug:slug>
    path('<slug:slug>/', views.detalhe_noticia, name='detalhe_noticia'),
]