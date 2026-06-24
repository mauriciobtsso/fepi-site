# painel/forms/noticias.py
from django import forms
from noticias.models import Noticia

class NoticiaForm(forms.ModelForm):
    # 🔴 O GOLPE DE MESTRE: Sobrescrevemos o campo inteiro fora do Meta!
    # Isso impede o Django de consultar a biblioteca problemática para gerar o campo.
    conteudo_blocos = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'id_conteudo_blocos'}),
        required=False
    )

    class Meta:
        model = Noticia
        fields = ['titulo', 'resumo', 'conteudo_blocos', 'imagem', 'data_publicacao', 'autor']
        
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título da Notícia'}),
            'resumo': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Breve resumo...'}),
            'autor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Autor da Matéria'}),
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'data_publicacao': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            # Removi o 'conteudo_blocos' daqui, pois já tratamos dele lá em cima!
        }
        
        labels = {
            'titulo': 'Título',
            'resumo': 'Resumo (Aparece na lista)',
            'autor': 'Autor',
            'imagem': 'Imagem de Capa',
            'data_publicacao': 'Data e Hora',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.data_publicacao:
            self.fields['data_publicacao'].initial = self.instance.data_publicacao.strftime('%Y-%m-%dT%H:%M')