from django.db import models
from ckeditor.fields import RichTextField
from cloudinary_storage.storage import RawMediaCloudinaryStorage

class Voluntario(models.Model):
    nome = models.CharField("Nome do Voluntário", max_length=200)
    cpf = models.CharField("CPF", max_length=14, blank=True, null=True)
    rg = models.CharField("RG/Exp.", max_length=50, blank=True, null=True)
    data_nascimento = models.DateField("Data de Nascimento", blank=True, null=True)
    
    nome_pai = models.CharField("Nome do Pai", max_length=200, blank=True, null=True)
    nome_mae = models.CharField("Nome da Mãe", max_length=200, blank=True, null=True)
    
    cep = models.CharField("CEP", max_length=10, blank=True, null=True)
    endereco = models.CharField("Logradouro", max_length=255, blank=True, null=True)
    numero = models.CharField("Número", max_length=10, blank=True, null=True)
    bairro = models.CharField("Bairro", max_length=100, blank=True, null=True)
    complemento = models.CharField("Complemento", max_length=100, blank=True, null=True)
    cidade_estado = models.CharField("Cidade/Estado", max_length=100, default="Teresina/PI", blank=True, null=True)
    
    email = models.EmailField("E-mail", blank=True, null=True)
    telefones = models.CharField("Telefone(s)", max_length=100, blank=True, null=True)
    
    atividade_profissional = models.CharField("Atividade Profissional", max_length=200, blank=True, null=True)
    tipo_servico = models.TextField("Tipo de Serviço a prestar", blank=True, null=True)
    dias_horarios = models.CharField("Dia(s) / Horário(s)", max_length=200, blank=True, null=True)
    
    data_inicio = models.DateField("Data de Início", blank=True, null=True)
    data_termino = models.DateField("Data de Término", blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

# --- NOVA TABELA PARA HISTÓRICO DE ARQUIVOS ---
class DocumentoVoluntario(models.Model):
    TIPOS_DOC = [
        ('Termo', 'Termo de Adesão Assinado'),
        ('Certidao', 'Certidão de Antecedentes'),
        ('Outro', 'Outro Documento'),
    ]
    
    voluntario = models.ForeignKey(Voluntario, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField("Tipo de Documento", max_length=50, choices=TIPOS_DOC)
    
    # 2. A MÁGICA ACONTECE AQUI: Informamos que o storage é para arquivos brutos (Raw)
    arquivo = models.FileField(
        upload_to='voluntarios/historico/', 
        storage=RawMediaCloudinaryStorage()
    )
    
    data_referencia = models.DateField("Data do Documento (Emissão)")
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_referencia']

class ModeloTermoVoluntario(models.Model):
    """Armazena o texto dinâmico do Termo de Adesão"""
    conteudo = RichTextField("Corpo do Termo", help_text="Use as tags disponíveis para puxar os dados do voluntário.")
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Modelo do Termo de Voluntário"
        
    def __str__(self):
        return "Configuração do Modelo de Termo"