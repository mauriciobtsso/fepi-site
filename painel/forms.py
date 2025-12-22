from django import forms
from noticias.models import Noticia
from core.models import ConfiguracaoHome
from intranet.models import DocumentoRestrito, CategoriaDocumento

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'resumo', 'conteudo', 'imagem', 'data_publicacao', 'autor']
        
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título da Notícia'}),
            'resumo': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Breve resumo...'}),
            
            # AQUI ESTÁ A CORREÇÃO: TextInput simples
            'autor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Autor da Matéria'}),
            
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'data_publicacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'titulo': 'Título',
            'resumo': 'Resumo (Aparece na lista)',
            'autor': 'Autor',
            'conteudo': 'Conteúdo Completo',
            'imagem': 'Imagem de Capa',
            'data_publicacao': 'Data',
        }

class PopupForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoHome
        # Adicionamos os campos de texto do botão e as datas
        fields = [
            'popup_titulo', 'popup_imagem', 'popup_link', 
            'popup_botao_texto', 'popup_inicio', 'popup_fim', 
            'popup_ativo'
        ]
        
        widgets = {
            'popup_titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título interno'}),
            'popup_imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'popup_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            
            # --- NOVOS CAMPOS ---
            'popup_botao_texto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Saiba Mais'}),
            
            # O type='datetime-local' cria o calendário com relógio do HTML5
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

    # Hackzinho necessário para o Django preencher o input de data corretamente ao editar
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.popup_inicio:
                self.fields['popup_inicio'].initial = self.instance.popup_inicio.strftime('%Y-%m-%dT%H:%M')
            if self.instance.popup_fim:
                self.fields['popup_fim'].initial = self.instance.popup_fim.strftime('%Y-%m-%dT%H:%M')

# Form para Criar/Editar Categorias
class CategoriaDocForm(forms.ModelForm):
    class Meta:
        model = CategoriaDocumento
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Atas de Reunião'}),
        }

# Form para Criar/Editar Documentos
class DocumentoForm(forms.ModelForm):
    class Meta:
        model = DocumentoRestrito
        fields = ['titulo', 'categoria', 'descricao', 'arquivo', 'link']
        
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }

