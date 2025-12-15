# core/admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    InformacaoContato, PaginaInstitucional, MembroDiretoria, ConfiguracaoHome,
    PostInstagram, TipoDiretoria, Cargo, ConfiguracaoYouTube
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
    list_display = ('__str__', 'titulo_banner', 'subtitulo_banner', 'popup_ativo')
    fieldsets = (
        ("Banner Principal", {'fields': ('titulo_banner', 'subtitulo_banner', 'imagem_banner')}),
        ("Pop-up (Marketing)", {
            'fields': (
                'popup_ativo', 'popup_titulo', 'popup_imagem', 'popup_link',
                'popup_botao_texto', 'popup_inicio', 'popup_fim'
            )
        }),
    )


@admin.register(ConfiguracaoYouTube)
class ConfiguracaoYouTubeAdmin(admin.ModelAdmin):
    readonly_fields = ('youtube_preview',)

    fieldsets = (
        ("YouTube", {
            "fields": ("youtube_mode", "youtube_channel_id", "youtube_video_id", "youtube_preview")
        }),
    )

    def youtube_preview(self, obj):
        if obj.youtube_mode == 'off':
            return "YouTube desligado."

        vid = (obj.youtube_video_id or "").strip()
        ch = (obj.youtube_channel_id or "").strip()

        if obj.youtube_mode == 'fixed':
            if not vid:
                return "Modo FIXO selecionado, mas sem Video ID."
            return format_html(
                '<iframe width="360" height="203" src="https://www.youtube.com/embed/{}" '
                'frameborder="0" allowfullscreen></iframe><br>'
                '<a href="https://www.youtube.com/watch?v={}" target="_blank" rel="noopener">Abrir no YouTube</a>',
                vid, vid
            )

        if not ch:
            return "Modo AUTOMÁTICO: informe o Channel ID."

        return format_html(
            'Modo AUTOMÁTICO ativo.<br>'
            '<a href="https://www.youtube.com/feeds/videos.xml?channel_id={}" target="_blank" rel="noopener">'
            'Abrir RSS do canal</a>',
            ch
        )

    youtube_preview.short_description = "Pré-visualização"


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
