from django.contrib import admin
from .models import DocumentoRestrito

@admin.register(DocumentoRestrito)
class DocumentoRestritoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'data_publicacao', 'link_arquivo')
    list_filter = ('categoria', 'data_publicacao')
    search_fields = ('titulo', 'descricao')

    def link_arquivo(self, obj):
        if obj.arquivo:
            return "Sim"
        return "Não"
    link_arquivo.short_description = "Arquivo Anexado"