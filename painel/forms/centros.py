# painel/forms/centros.py
from django import forms
from centros.models import Centro

class CentroForm(forms.ModelForm):
    class Meta:
        model = Centro
        fields = ['nome', 'tipo', 'foto', 'cnpj', 'data_fundacao', 'cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'telefone', 'site', 'latitude', 'longitude']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0001-00'}),
            'data_fundacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CEP'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nº'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'site': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }