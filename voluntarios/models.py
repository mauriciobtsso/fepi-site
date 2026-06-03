from django.db import models
from ckeditor.fields import RichTextField
from cloudinary_storage.storage import RawMediaCloudinaryStorage
from usuarios.models import Perfil # Trazendo o Cadastro Único

class DocumentoVoluntario(models.Model):
    TIPOS_DOC = [
        ('Termo', 'Termo de Adesão Assinado'),
        ('Certidao', 'Certidão de Antecedentes'),
        ('Outro', 'Outro Documento'),
    ]
    
    # Apontando para o Perfil Único (filtrando apenas quem é voluntário)
    voluntario = models.ForeignKey(
        Perfil, 
        on_delete=models.CASCADE, 
        limit_choices_to={'is_voluntario': True},
        related_name='documentos_voluntario',
        verbose_name="Voluntário"
    )
    tipo = models.CharField("Tipo de Documento", max_length=50, choices=TIPOS_DOC)
    
    arquivo = models.FileField(
        upload_to='voluntarios/historico/', 
        storage=RawMediaCloudinaryStorage()
    )
    
    data_referencia = models.DateField("Data do Documento (Emissão)")
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento de Voluntário"
        verbose_name_plural = "Documentos de Voluntários"
        ordering = ['-data_referencia']
        
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.voluntario.nome_razao_social}"

class ModeloTermoVoluntario(models.Model):
    """Armazena o texto dinâmico do Termo de Adesão"""
    conteudo = RichTextField("Corpo do Termo", help_text="Use as tags disponíveis para puxar os dados do voluntário.")
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Modelo do Termo de Voluntário"
        
    def __str__(self):
        return "Configuração do Modelo de Termo"