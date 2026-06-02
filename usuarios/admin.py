from django.contrib import admin
from .models import Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    # As colunas que vão aparecer na tabela principal
    list_display = ('usuario_nome', 'nome_razao_social', 'tipo', 'status', 'is_colunista', 'centro_vinculado')
    
    # Filtros laterais para facilitar a vida da diretoria
    list_filter = ('status', 'tipo', 'is_colunista')
    
    # Barra de pesquisa (busca por nome, username do Django, ou CPF/CNPJ)
    search_fields = ('user__username', 'nome_razao_social', 'cpf_cnpj')
    
    # Define quais campos podem ser editados diretamente na tabela (sem precisar abrir o cadastro)
    list_editable = ('status', 'is_colunista')
    
    # Organização visual dentro da página de edição do Perfil
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

    # Função extra para mostrar o username do Django na tabela
    def usuario_nome(self, obj):
        return obj.user.username
    usuario_nome.short_description = 'Usuário (Login)'