# painel/forms/equipe.py
from django import forms
from core.models import Cargo, TipoDiretoria, MembroDiretoria

class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['nome']
        widgets = {'nome': forms.TextInput(attrs={'class': 'form-control'})}

class TipoDiretoriaForm(forms.ModelForm):
    class Meta:
        model = TipoDiretoria
        fields = ['nome', 'descricao', 'ordem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class MembroDiretoriaForm(forms.ModelForm):
    class Meta:
        model = MembroDiretoria
        fields = ['nome', 'cargo', 'tipo', 'telefone', 'email', 'ordem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}), 
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ordem de exibição'}),
        }