from django import forms
from core.models import Coluna
from usuarios.models import Perfil

class ColunaIntranetForm(forms.ModelForm):
    class Meta:
        model = Coluna
        # Omitimos o status, autor e slug, pois o sistema preencherá automaticamente
        fields = ['titulo', 'resumo', 'conteudo', 'imagem_capa']
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control form-control-lg', 
                'placeholder': 'Ex: A visão espírita sobre o perdão',
                'maxlength': '200',  # Trava o limite no navegador
                'id': 'id_titulo'
            }),
            'resumo': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Escreva um parágrafo chamativo para a página inicial...',
                'maxlength': '400',  # Trava o limite no navegador
                'id': 'id_resumo'
            }),
            'imagem_capa': forms.FileInput(attrs={'class': 'form-control'}),
        }

class IntranetVoluntarioForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['atividade_profissional', 'tipo_servico', 'dias_horarios']
        widgets = {
            'atividade_profissional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Professor, Advogado, Estudante...'}),
            'tipo_servico': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descreva como gostaria de ajudar (ex: Recepção, Livraria, Comunicação...)'}),
            'dias_horarios': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Sábados pela manhã, Terças à noite...'}),
        }