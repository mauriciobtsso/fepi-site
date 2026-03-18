from django import forms
from .models import ModeloTermoVoluntario
from .models import Voluntario, DocumentoVoluntario

class VoluntarioForm(forms.ModelForm):
    class Meta:
        model = Voluntario
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_inicio': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_termino': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'tipo_servico': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class DocumentoVoluntarioForm(forms.ModelForm):
    class Meta:
        model = DocumentoVoluntario
        fields = ['tipo', 'data_referencia', 'arquivo']
        widgets = {
            'data_referencia': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})

class ModeloTermoForm(forms.ModelForm):
    class Meta:
        model = ModeloTermoVoluntario
        fields = ['conteudo']