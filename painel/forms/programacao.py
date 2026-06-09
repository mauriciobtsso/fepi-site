# painel/forms/programacao.py
from django import forms
from ckeditor.widgets import CKEditorWidget
from programacao.models import AtividadeSemanal, Doutrinaria, CursoEvento

class AtividadeSemanalForm(forms.ModelForm):
    class Meta:
        model = AtividadeSemanal
        fields = ['dia', 'horario', 'nome', 'descricao']
        widgets = {
            'dia': forms.Select(attrs={'class': 'form-select'}),
            'horario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 19h30 às 21h00'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': CKEditorWidget(attrs={'class': 'form-control'}),
        }

class DoutrinariaForm(forms.ModelForm):
    class Meta:
        model = Doutrinaria
        fields = ['data_hora', 'tema', 'palestrante', 'imagem', 'descricao']
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'tema': forms.TextInput(attrs={'class': 'form-control'}),
            'palestrante': forms.TextInput(attrs={'class': 'form-control'}),
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'descricao': CKEditorWidget(), 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.data_hora:
            self.fields['data_hora'].initial = self.instance.data_hora.strftime('%Y-%m-%dT%H:%M')

class CursoEventoForm(forms.ModelForm):
    class Meta:
        model = CursoEvento
        fields = ['titulo', 'data_evento', 'local', 'link_inscricao', 'imagem', 'descricao']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'data_evento': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'local': forms.TextInput(attrs={'class': 'form-control', 'value': 'Sede da FEPI'}),
            'link_inscricao': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Link do Google Forms ou WhatsApp'}),
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'descricao': CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.data_evento:
            self.fields['data_evento'].initial = self.instance.data_evento.strftime('%Y-%m-%dT%H:%M')