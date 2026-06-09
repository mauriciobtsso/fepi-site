# painel/forms/site.py
from django import forms
from ckeditor.widgets import CKEditorWidget
from core.models import ConfiguracaoHome, ConfiguracaoYouTube, PostInstagram, PaginaInstitucional, InformacaoContato

class PopupForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoHome
        fields = [
            'popup_titulo', 'popup_imagem', 'popup_link', 
            'popup_botao_texto', 'popup_inicio', 'popup_fim', 
            'popup_ativo'
        ]
        
        widgets = {
            'popup_titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título interno'}),
            'popup_imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'popup_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'popup_botao_texto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Saiba Mais'}),
            'popup_inicio': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}, 
                format='%Y-%m-%dT%H:%M'
            ),
            'popup_fim': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}, 
                format='%Y-%m-%dT%H:%M'
            ),
            'popup_ativo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'width: 25px; height: 25px;'}),
        }
        labels = {
            'popup_titulo': 'Título do Aviso',
            'popup_imagem': 'Imagem do Pop-up',
            'popup_link': 'Link de Destino',
            'popup_botao_texto': 'Texto do Botão',
            'popup_inicio': 'Começar a exibir em:',
            'popup_fim': 'Parar de exibir em:',
            'popup_ativo': 'Ativar Pop-up?',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.popup_inicio:
                self.fields['popup_inicio'].initial = self.instance.popup_inicio.strftime('%Y-%m-%dT%H:%M')
            if self.instance.popup_fim:
                self.fields['popup_fim'].initial = self.instance.popup_fim.strftime('%Y-%m-%dT%H:%M')

class YoutubeConfigForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoYouTube
        fields = ['youtube_mode', 'youtube_channel_id', 'youtube_video_id']
        widgets = {
            'youtube_mode': forms.Select(attrs={'class': 'form-select'}),
            'youtube_channel_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: UC...'}),
            'youtube_video_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: dQw4w9WgXcQ'}),
        }

class PostInstagramForm(forms.ModelForm):
    class Meta:
        model = PostInstagram
        fields = ['imagem', 'link', 'legenda']
        widgets = {
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/p/...'}),
            'legenda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição curta para acessibilidade'}),
        }

class PaginaInstitucionalForm(forms.ModelForm):
    class Meta:
        model = PaginaInstitucional
        fields = ['titulo', 'frase_destaque', 'ano_inicio', 'ano_fim', 'conteudo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'frase_destaque': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_inicio': forms.NumberInput(attrs={'class': 'form-control', 'style':'width: 100px; display:inline-block;'}),
            'ano_fim': forms.NumberInput(attrs={'class': 'form-control', 'style':'width: 100px; display:inline-block;'}),
            'conteudo': CKEditorWidget(),
79	        }
80	
81	class InformacaoContatoForm(forms.ModelForm):
82	    class Meta:
83	        model = InformacaoContato
84	        fields = ['endereco', 'cidade', 'cep', 'telefone', 'email', 'horario_livraria']
85	        widgets = {
86	            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
87	            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
88	            'cep': forms.TextInput(attrs={'class': 'form-control'}),
89	            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
90	            'email': forms.EmailInput(attrs={'class': 'form-control'}),
91	            'horario_livraria': forms.TextInput(attrs={'class': 'form-control'}),
92	        }