# core/admin.py
from django.contrib import admin
from .models import (
    InformacaoContato, PaginaInstitucional, MembroDiretoria, ConfiguracaoHome,
    PostInstagram, TipoDiretoria, Cargo
)

admin.site.register(TipoDiretoria)
admin.site.register(Cargo)

@admin.register(PostInstagram)
class PostInstagramAdmin(admin.ModelAdmin):
    list_display = ("legenda", "data_post", "link")
    list_filter = ("data_post",)
    search_fields = ("legenda", "link")
    ordering = ("-data_post",)

@admin.register(InformacaoContato)
class InformacaoContatoAdmin(admin.ModelAdmin):
    list_display = ('endereco', 'telefone', 'horario_livraria')

@admin.register(ConfiguracaoHome)
class ConfiguracaoHomeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'titulo_banner', 'youtube_video_id')

@admin.register(PaginaInstitucional)
class PaginaInstitucionalAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ano_inicio', 'ano_fim')
    fieldsets = (
        ('Conteúdo Principal', {'fields': ('titulo', 'frase_destaque', 'conteudo')}),
        ('Gestão Atual', {'fields': ('ano_inicio', 'ano_fim')}),
    )

@admin.register(MembroDiretoria)
class MembroDiretoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'tipo', 'ordem', 'telefone')
    list_filter = ('tipo', 'cargo')
    search_fields = ('nome', 'cargo__nome', 'tipo__nome')
    list_editable = ('ordem',)

    fieldsets = (
        (None, {'fields': ('nome', 'cargo', 'tipo', 'ordem')}),
        ('Contato e Informações', {'fields': ('telefone', 'email')}),
    )
