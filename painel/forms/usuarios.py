# painel/forms/usuarios.py
from django import forms
from usuarios.models import Perfil

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        exclude = ['user']
        widgets = {
            'data_nascimento_fundacao': forms.DateInput(attrs={'type': 'date'}),
        }