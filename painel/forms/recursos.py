# painel/forms/recursos.py
from django import forms
from recursos.models import SecaoLink, LinkItem

class SecaoLinkForm(forms.ModelForm):
    class Meta:
        model = SecaoLink
        fields = ['nome', 'icone_fa', 'ordem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'icone_fa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: fa-solid fa-file-pdf'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class LinkItemForm(forms.ModelForm):
    class Meta:
        model = LinkItem
        fields = ['secao', 'titulo', 'url', 'is_download', 'descricao']
        widgets = {
            'secao': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Link ou URL do arquivo'}),
            'is_download': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'width: 20px; height: 20px;'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }