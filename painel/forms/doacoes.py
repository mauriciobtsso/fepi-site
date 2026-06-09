# painel/forms/doacoes.py
from django import forms
from ckeditor.widgets import CKEditorWidget
from doacoes.models import FormaDoacao, PaginaDoacaoConfig

class FormaDoacaoForm(forms.ModelForm):
    class Meta:
        model = FormaDoacao
        fields = ['titulo', 'tipo', 'chave_pix', 'qr_code', 'banco', 'agencia', 'conta', 'descricao', 'ordem']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'chave_pix': forms.TextInput(attrs={'class': 'form-control'}),
            'qr_code': forms.FileInput(attrs={'class': 'form-control'}),
            'banco': forms.TextInput(attrs={'class': 'form-control'}),
            'agencia': forms.TextInput(attrs={'class': 'form-control'}),
            'conta': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PaginaDoacaoConfigForm(forms.ModelForm):
    class Meta:
        model = PaginaDoacaoConfig
        fields = '__all__'
        widgets = {
            'titulo_principal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Ajude a FEPI'}),
            'texto_apelo': CKEditorWidget(),
            'imagem_capa': forms.FileInput(attrs={'class': 'form-control'}),
            'titulo_socio': forms.TextInput(attrs={'class': 'form-control'}),
            'texto_socio': CKEditorWidget(),
            'link_socio': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }