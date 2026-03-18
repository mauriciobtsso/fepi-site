from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_voluntarios, name='listar_voluntarios'),
    path('novo/', views.cadastrar_voluntario, name='cadastrar_voluntario'),
    path('editar/<int:pk>/', views.editar_voluntario, name='editar_voluntario'),
    path('excluir/<int:pk>/', views.excluir_voluntario, name='excluir_voluntario'),
    path('imprimir/<int:pk>/', views.imprimir_termo, name='imprimir_termo'),
    path('modelo-termo/', views.editar_modelo_termo, name='editar_modelo_termo'),
    
    # Novas rotas de Histórico
    path('<int:pk>/documentos/', views.documentos_voluntario, name='documentos_voluntario'),
    path('documentos/excluir/<int:pk>/', views.excluir_documento_voluntario, name='excluir_documento_voluntario'),
]