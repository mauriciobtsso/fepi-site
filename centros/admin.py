from django.contrib import admin
from .models import Centro

@admin.register(Centro)
class CentroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'bairro', 'telefone', 'site')
    list_filter = ('tipo', 'cidade', 'estado')
    search_fields = ('nome', 'cnpj', 'bairro', 'cidade')
    
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'tipo', 'foto', 'cnpj', 'data_fundacao')
        }),
        ('Localização (Digite o CEP para preencher)', {
            'fields': ('cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'latitude', 'longitude')
        }),
        ('Contato', {
            'fields': ('telefone', 'site')
        }),
    )

    class Media:
        # Carrega o script responsável pelo ViaCEP e Máscaras
        js = ('js/admin_cep.js',)