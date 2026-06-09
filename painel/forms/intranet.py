# painel/forms/intranet.py
from django import forms
from intranet.models import DocumentoRestrito, CategoriaDocumento

class CategoriaDocForm(forms.ModelForm):
    class Meta:
        model = CategoriaDocumento
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Atas de Reunião'}),
        }

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = DocumentoRestrito
        fields = ['titulo', 'categoria', 'descricao', 'arquivo', 'link']
        
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }