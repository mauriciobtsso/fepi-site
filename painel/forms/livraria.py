# painel/forms/livraria.py
from django import forms
from ckeditor.widgets import CKEditorWidget
from livraria.models import Livro, Categoria, LivrariaConfig

class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ['codigo', 'titulo', 'autor', 'categoria', 'preco', 'quantidade_estoque', 'capa', 'ativo_na_vitrine', 'destaque_home', 'disponivel', 'descricao']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ISBN ou Ref interna'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantidade_estoque': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'capa': forms.FileInput(attrs={'class': 'form-control'}),
            'ativo_na_vitrine': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'width: 20px; height: 20px;'}),
            'destaque_home': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'width: 20px; height: 20px;'}),
            'disponivel': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'width: 20px; height: 20px;'}),
            'descricao': CKEditorWidget(),
        }

class CategoriaLivroForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Romance, Estudo, Infantil'}),
        }

class LivrariaConfigForm(forms.ModelForm):
    class Meta:
        model = LivrariaConfig
        fields = ['logo', 'whatsapp', 'instagram_url', 'instagram_widget_code']
        widgets = {
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 5535912345678'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/...'}),
            'instagram_widget_code': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Cole aqui o iframe do SnapWidget se tiver'}),
        }