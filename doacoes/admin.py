from django.contrib import admin
from .models import FormaDoacao

@admin.register(FormaDoacao)
class FormaDoacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'ordem')
    list_editable = ('ordem',)
    list_filter = ('tipo',)
    search_fields = ('titulo', 'chave_pix', 'conta')

    fieldsets = (
        ('Geral', {'fields': ('titulo', 'tipo', 'ordem', 'descricao')}),
        ('Detalhes Bancários/PIX', {'fields': ('chave_pix', 'qr_code', 'banco', 'agencia', 'conta')}), # <--- Adicionado 'qr_code'
    )