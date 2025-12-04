from django.contrib import admin
from .models import SecaoLink, LinkItem

@admin.register(SecaoLink)
class SecaoLinkAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem', 'icone_fa')
    list_editable = ('ordem',)

@admin.register(LinkItem)
class LinkItemAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'secao', 'is_download', 'url')
    list_filter = ('secao', 'is_download')
    search_fields = ('titulo', 'descricao')