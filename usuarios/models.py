from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    TIPO_USUARIO = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Instituição (Centro Espírita)'),
    ]

    STATUS_APROVACAO = [
        ('PENDENTE', 'Aguardando Aprovação'),
        ('APROVADO', 'Aprovado'),
        ('RECUSADO', 'Recusado'),
    ]

    # Relacionamento 1-para-1 com o Usuário padrão do Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    
    # Dados de Identificação
    tipo = models.CharField(max_length=2, choices=TIPO_USUARIO, default='PF', verbose_name="Tipo de Conta")
    status = models.CharField(max_length=10, choices=STATUS_APROVACAO, default='PENDENTE', verbose_name="Status de Cadastro")
    
    nome_razao_social = models.CharField(max_length=255, verbose_name="Nome Completo / Razão Social", blank=True, null=True)
    cpf_cnpj = models.CharField(max_length=18, verbose_name="CPF / CNPJ", blank=True, null=True)
    data_nascimento_fundacao = models.DateField(verbose_name="Data de Nascimento / Fundação", blank=True, null=True)
    
    # Contato
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone/WhatsApp")
    site = models.URLField(verbose_name="Site Institucional", blank=True, null=True)
    
    # Endereço Completo
    cep = models.CharField(max_length=9, verbose_name="CEP", blank=True, null=True)
    logradouro = models.CharField(max_length=255, verbose_name="Logradouro", blank=True, null=True)
    numero = models.CharField(max_length=20, verbose_name="Número", blank=True, null=True)
    complemento = models.CharField(max_length=100, verbose_name="Complemento", blank=True, null=True)
    bairro = models.CharField(max_length=100, verbose_name="Bairro", blank=True, null=True)
    cidade = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    estado = models.CharField(max_length=2, verbose_name="UF", blank=True, null=True)
    
    # Permissões e Vínculos da FEPI
    is_colunista = models.BooleanField(default=False, verbose_name="É Colunista?")
    centro_vinculado = models.ForeignKey(
        'centros.Centro', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='responsaveis',
        verbose_name="Centro Espírita Vinculado"
    )

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        return f"{self.nome_razao_social or self.user.username} ({self.get_tipo_display()})"


# --- SINAIS (MÁGICA DO DJANGO) ---
@receiver(post_save, sender=User)
def gerenciar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        # Cria o perfil automaticamente se for um usuário novo
        Perfil.objects.get_or_create(user=instance)
    else:
        # Na hora de salvar (ex: ao fazer login), só salva o perfil se ele existir
        if hasattr(instance, 'perfil'):
            instance.perfil.save()
        else:
            # Se for um superuser antigo que não tem perfil, cria um agora
            Perfil.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def salvar_perfil_usuario(sender, instance, **kwargs):
    instance.perfil.save()