from django.contrib import admin
from .models import Noticia

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    # Agora 'foi_publicada' existe e pode ser exibido
    list_display = ('titulo', 'data_publicacao', 'autor', 'foi_publicada')
    list_filter = ('data_publicacao', 'autor', 'foi_publicada') 
    search_fields = ('titulo', 'conteudo', 'autor')

    fieldsets = (
        (None, {'fields': ('titulo', 'resumo', 'conteudo', 'autor', 'imagem')}),
        ('Status de Publicação', {'fields': ('foi_publicada', 'data_publicacao')}), # Campo 'foi_publicada'
    )