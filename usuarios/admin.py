from django.contrib import admin
from .models import Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario_nome', 'nome_razao_social', 'tipo', 'status', 'is_colunista', 'centro_vinculado')
    list_filter = ('status', 'tipo', 'is_colunista')
    search_fields = ('user__username', 'nome_razao_social', 'cpf_cnpj')
    list_editable = ('status', 'is_colunista')
    
    fieldsets = (
        ('Usuário Vinculado', {
            'fields': ('user', 'status', 'tipo')
        }),
        ('Dados de Identificação', {
            'fields': ('nome_razao_social', 'cpf_cnpj', 'data_nascimento_fundacao')
        }),
        ('Contato e Endereço', {
            'fields': ('telefone', 'site', 'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado')
        }),
        ('Permissões e Vínculos FEPI', {
            'fields': ('is_colunista', 'centro_vinculado')
        }),
    )

    def usuario_nome(self, obj):
        return obj.user.username
    usuario_nome.short_description = 'Usuário (Login)'