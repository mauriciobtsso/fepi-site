from django.contrib import admin
from .models import Centro

@admin.register(Centro)
class CentroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'bairro', 'telefone', 'site') # Adicionei site na lista
    list_filter = ('tipo', 'cidade', 'estado')
    search_fields = ('nome', 'cnpj', 'bairro')
    
    # Aqui definimos a ordem e os grupos do formulário
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'tipo', 'foto', 'cnpj', 'data_fundacao')
        }),
        ('Localização (Digite o CEP para preencher)', {
            'fields': ('cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado')
        }),
        ('Contato', {
            'fields': ('telefone', 'site') # <--- AQUI ESTÁ ELE! Agora vai aparecer.
        }),
    )

    # Carrega o script que busca o CEP
    class Media:
        js = ('js/admin_cep.js',)