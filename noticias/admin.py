from django.contrib import admin
from .models import Noticia

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_publicacao', 'slug') # Adicionei slug aqui para veres
    search_fields = ('titulo', 'conteudo')
    
    # Esta linha faz a magia no painel admin:
    prepopulated_fields = {'slug': ('titulo',)}