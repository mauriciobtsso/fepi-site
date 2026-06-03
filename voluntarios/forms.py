from django import forms
from .models import ModeloTermoVoluntario, DocumentoVoluntario
from usuarios.models import Perfil # Importando o Cadastro Único

class VoluntarioForm(forms.ModelForm):
    class Meta:
        model = Perfil # Agora aponta para a tabela unificada
        
        # Selecionamos apenas os campos que fazem sentido para a tela da secretaria de voluntários
        fields = [
            'nome_razao_social', 'cpf_cnpj', 'rg', 'data_nascimento_fundacao',
            'nome_pai', 'nome_mae', 'cep', 'logradouro', 'numero', 'complemento', 
            'bairro', 'cidade', 'estado', 'telefone', 'site', 
            'atividade_profissional', 'tipo_servico', 'dias_horarios', 
            'data_inicio_voluntariado', 'data_termino_voluntariado'
        ]
        
        widgets = {
            'data_nascimento_fundacao': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_inicio_voluntariado': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_termino_voluntariado': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tipo_servico': forms.Textarea(attrs={'rows': 2}),
        }
        
        # Opcional: Alterar os labels (nomes) que aparecem na tela para ficar amigável
        labels = {
            'nome_razao_social': 'Nome Completo',
            'cpf_cnpj': 'CPF',
            'data_nascimento_fundacao': 'Data de Nascimento',
            'logradouro': 'Endereço (Rua/Av)',
            'telefone': 'Telefone / WhatsApp'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class DocumentoVoluntarioForm(forms.ModelForm):
    class Meta:
        model = DocumentoVoluntario
        fields = ['tipo', 'data_referencia', 'arquivo']
        widgets = {
            'data_referencia': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})

class ModeloTermoForm(forms.ModelForm):
    class Meta:
        model = ModeloTermoVoluntario
        fields = ['conteudo']