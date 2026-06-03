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
    
    # --- CHAVES DE PERMISSÃO E PAPÉIS ---
    is_colunista = models.BooleanField(default=False, verbose_name="É Colunista?")
    is_voluntario = models.BooleanField(default=False, verbose_name="É Voluntário?")
    
    # --- DADOS UNIVERSAIS ---
    tipo = models.CharField(max_length=2, choices=TIPO_USUARIO, default='PF', verbose_name="Tipo de Conta")
    status = models.CharField(max_length=10, choices=STATUS_APROVACAO, default='PENDENTE', verbose_name="Status de Cadastro")
    
    nome_razao_social = models.CharField(max_length=255, verbose_name="Nome Completo / Razão Social", blank=True, null=True)
    cpf_cnpj = models.CharField(max_length=18, verbose_name="CPF / CNPJ", blank=True, null=True)
    rg = models.CharField("RG/Exp.", max_length=50, blank=True, null=True)
    data_nascimento_fundacao = models.DateField(verbose_name="Data de Nascimento / Fundação", blank=True, null=True)
    
    # Filiação
    nome_pai = models.CharField("Nome do Pai", max_length=200, blank=True, null=True)
    nome_mae = models.CharField("Nome da Mãe", max_length=200, blank=True, null=True)
    
    # Contato e Mídia
    telefone = models.CharField(max_length=100, blank=True, null=True, verbose_name="Telefone(s)/WhatsApp")
    site = models.URLField(verbose_name="Site Institucional", blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='autores_perfis/', null=True, blank=True, verbose_name="Foto de Perfil")
    
    # Endereço Completo
    cep = models.CharField(max_length=10, verbose_name="CEP", blank=True, null=True)
    logradouro = models.CharField(max_length=255, verbose_name="Logradouro", blank=True, null=True)
    numero = models.CharField(max_length=20, verbose_name="Número", blank=True, null=True)
    complemento = models.CharField(max_length=100, verbose_name="Complemento", blank=True, null=True)
    bairro = models.CharField(max_length=100, verbose_name="Bairro", blank=True, null=True)
    cidade = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    estado = models.CharField(max_length=2, verbose_name="UF", blank=True, null=True)
    
    # --- DADOS ESPECÍFICOS (VOLUNTARIADO) ---
    atividade_profissional = models.CharField("Atividade Profissional", max_length=200, blank=True, null=True)
    tipo_servico = models.TextField("Tipo de Serviço a prestar", blank=True, null=True)
    dias_horarios = models.CharField("Dia(s) / Horário(s) Disponíveis", max_length=200, blank=True, null=True)
    data_inicio_voluntariado = models.DateField("Data de Início no Voluntariado", blank=True, null=True)
    data_termino_voluntariado = models.DateField("Data de Término no Voluntariado", blank=True, null=True)
    
    # --- VÍNCULOS INSTITUCIONAIS ---
    centro_vinculado = models.ForeignKey(
        'centros.Centro', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='responsaveis',
        verbose_name="Centro Espírita Vinculado"
    )

    class Meta:
        verbose_name = "Perfil Único"
        verbose_name_plural = "Perfis Únicos"

    def __str__(self):
        return f"{self.nome_razao_social or self.user.username} ({self.get_tipo_display()})"


# --- SINAIS (MÁGICA DO DJANGO) ---
@receiver(post_save, sender=User)
def gerenciar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Garante que todo User criado tenha um Perfil atrelado automaticamente.
    """
    if created:
        Perfil.objects.get_or_create(user=instance)
    else:
        if hasattr(instance, 'perfil'):
            instance.perfil.save()
        else:
            Perfil.objects.get_or_create(user=instance)