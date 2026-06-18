from django.contrib import admin
from .models import Perfil
from core.utils import enviar_email_sistema

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

    def save_model(self, request, obj, form, change):
        """
        Intercepta o salvamento do perfil no Admin.
        Se o administrador mudar o status para 'APROVADO', o usuário do Django 
        é ativado e ele recebe o e-mail de acesso.
        """
        if change and 'status' in form.changed_data:
            # Verifica se o novo status alterado é APROVADO
            if obj.status == 'APROVADO':
                # Captura o usuário vinculado do Django
                usuario_django = obj.user
                
                # Se a conta ainda estiver desativada, nós ativamos!
                if not usuario_django.is_active:
                    usuario_django.is_active = True
                    usuario_django.save()
                    
                    # Dispara o e-mail transacional de cadastro autorizado
                    enviar_email_sistema(
                        assunto="Seu acesso ao Portal FEPI foi Liberado! 🎉",
                        corpo="",
                        destinatarios=[usuario_django.email],
                        template_name="emails/cadastro_autorizado.html",
                        context={
                            "nome": obj.nome_razao_social,
                            "email": usuario_django.email
                        }
                    )
        
        # Executa o salvamento padrão do modelo
        super().save_model(request, obj, form, change)