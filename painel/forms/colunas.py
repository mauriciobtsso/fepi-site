# painel/forms/colunas.py
from django import forms
from django.db.models import Q
from django.contrib.auth.models import User
from core.models import Coluna

class ColunaForm(forms.ModelForm):
    class Meta:
        model = Coluna
        fields = [
            'titulo', 'resumo', 'autor_usuario', 'nome_autor', 'instituicao_autor', 
            'imagem_capa', 'conteudo', 'data_publicacao', 'status'
        ]
        widgets = {
            'data_publicacao': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_autor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preencher apenas se não for associado'}),
            'instituicao_autor': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra a lista de associados
        self.fields['autor_usuario'].queryset = User.objects.filter(Q(perfil__is_colunista=True) | Q(is_superuser=True))
        
        # Aplica a classe do Bootstrap a todos os campos
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        self.fields['status'].widget.attrs['class'] = 'form-select'
        self.fields['autor_usuario'].widget.attrs['class'] = 'form-select'

    def clean(self):
        cleaned_data = super().clean()
        autor_usuario = cleaned_data.get('autor_usuario')
        nome_autor = cleaned_data.get('nome_autor')
        
        if not autor_usuario and not nome_autor:
            raise forms.ValidationError("Você deve selecionar um Associado ou preencher o Nome do Autor manualmente.")
        return cleaned_data