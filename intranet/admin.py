from django.contrib import admin
from .models import DocumentoRestrito

@admin.register(DocumentoRestrito)
class DocumentoRestritoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'data_publicacao', 'tem_arquivo', 'tem_link')
    list_filter = ('categoria', 'data_publicacao')
    search_fields = ('titulo', 'descricao')

    def tem_arquivo(self, obj):
        return bool(obj.arquivo)
    tem_arquivo.boolean = True
    tem_arquivo.short_description = "Arquivo?"

    def tem_link(self, obj):
        return bool(obj.link)
    tem_link.boolean = True
    tem_link.short_description = "Link?"