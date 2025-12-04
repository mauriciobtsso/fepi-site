from django.contrib import admin
from .models import (
    InformacaoContato, PaginaInstitucional, MembroDiretoria, ConfiguracaoHome,
    PostInstagram, TipoDiretoria, Cargo # Importações de todos os modelos
)

# 1. REGISTRO DE MODELOS DINÂMICOS E SINGLETONS SIMPLES

# Modelos que o usuário cria e edita (opções para as Foreign Keys)
admin.site.register(TipoDiretoria)     
admin.site.register(Cargo)             
admin.site.register(PostInstagram)

# Singleton de Contato
@admin.register(InformacaoContato)
class InformacaoContatoAdmin(admin.ModelAdmin):
    list_display = ('endereco', 'telefone', 'horario_livraria')

# 2. CONFIGURAÇÕES AVANÇADAS

# Configuração da Home (Banner/YouTube)
@admin.register(ConfiguracaoHome)
class ConfiguracaoHomeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'titulo_banner', 'youtube_video_id')
    
# Página Institucional (Texto da História e Anos de Gestão)
@admin.register(PaginaInstitucional)
class PaginaInstitucionalAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ano_inicio', 'ano_fim')
    fieldsets = (
        ('Conteúdo Principal', {'fields': ('titulo', 'frase_destaque', 'conteudo')}),
        ('Gestão Atual', {'fields': ('ano_inicio', 'ano_fim')}),
    )

# Membros da Diretoria e Departamentos (Tabela complexa)
@admin.register(MembroDiretoria)
class MembroDiretoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'tipo', 'ordem', 'telefone') # Mostra cargo e tipo dinâmicos
    # Filtros por campo relacionado (ForeignKey)
    list_filter = ('tipo', 'cargo') 
    search_fields = ('nome', 'cargo__nome', 'tipo__nome')
    list_editable = ('ordem',)
    
    fieldsets = (
        (None, {'fields': ('nome', 'cargo', 'tipo', 'ordem')}),
        ('Contato e Informações', {'fields': ('telefone', 'email')}),
    )