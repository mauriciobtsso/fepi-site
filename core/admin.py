from django.contrib import admin
from .models import InformacaoContato, PaginaInstitucional, MembroDiretoria, ConfiguracaoHome, PostInstagram

# ... (outros registros)

admin.site.register(PaginaInstitucional)
admin.site.register(ConfiguracaoHome)
admin.site.register(PostInstagram)

@admin.register(MembroDiretoria)
class DiretoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'tipo', 'ordem')
    list_filter = ('tipo',)
    list_editable = ('ordem',) # Permite mudar a ordem rápido