# painel/forms/usuarios.py
from django import forms
from usuarios.models import Perfil, PaginaSejaMembro # <-- ADICIONADO PaginaSejaMembro
from ckeditor_uploader.widgets import CKEditorUploadingWidget # <-- ADICIONADO para texto rico com upload

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        exclude = ['user']
        widgets = {
            'data_nascimento_fundacao': forms.DateInput(attrs={'type': 'date'}),
        }

# 🔴 NOVO FORM: Página Seja Membro
class PaginaSejaMembroForm(forms.ModelForm):
    class Meta:
        model = PaginaSejaMembro
        fields = ['conteudo']
        widgets = {
            'conteudo': CKEditorUploadingWidget(),
        }
        labels = {
            'conteudo': 'Texto da Página (História, Missão e Motivos para Associação)'
        }