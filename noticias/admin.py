from django.contrib import admin
from .models import Noticia

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    # Campos que aparecem na lista de notícias
    list_display = ('titulo', 'data_publicacao', 'autor', 'foi_publicada')
    list_filter = ('data_publicacao', 'autor', 'foi_publicada') 
    search_fields = ('titulo', 'conteudo', 'autor')

    # Campos que o usuário PODE ver mas NÃO PODE editar
    readonly_fields = ('data_publicacao',) 

    fieldsets = (
        ('Conteúdo Principal', {'fields': ('titulo', 'resumo', 'conteudo', 'autor', 'imagem')}),
        ('Status de Publicação', {'fields': ('foi_publicada', 'data_publicacao')}), # <-- Data agora pode ser lida
    )