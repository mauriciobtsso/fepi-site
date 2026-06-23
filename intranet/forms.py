# intranet/forms.py
from django import forms
from core.models import Coluna
from usuarios.models import Perfil
from blogs.models import PostBlog
from django_editorjs_fields import EditorJsWidget

class ColunaIntranetForm(forms.ModelForm):
    class Meta:
        model = Coluna
        # Omitimos o status, autor e slug, pois o sistema preencherá automaticamente
        fields = ['titulo', 'resumo', 'conteudo', 'imagem_capa']
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control form-control-lg', 
                'placeholder': 'Ex: A visão espírita sobre o perdão',
                'maxlength': '200',  # Trava o limite no navegador
                'id': 'id_titulo'
            }),
            'resumo': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Escreva um parágrafo chamativo para a página inicial...',
                'maxlength': '400',  # Trava o limite no navegador
                'id': 'id_resumo'
            }),
            'imagem_capa': forms.FileInput(attrs={'class': 'form-control'}),
        }

class IntranetVoluntarioForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['atividade_profissional', 'tipo_servico', 'dias_horarios']
        widgets = {
            'atividade_profissional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Professor, Advogado, Estudante...'}),
            'tipo_servico': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descreva como gostaria de ajudar (ex: Recepção, Livraria, Comunicação...)'}),
            'dias_horarios': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Sábados pela manhã, Terças à noite...'}),
        }

# --- NOVO: FORMULÁRIO DO BLOG DE DEPARTAMENTO ---
class IntranetPostBlogForm(forms.ModelForm):
    class Meta:
        model = PostBlog
        # Omitimos 'departamento', 'autor' e 'slug' por segurança
        fields = ['categoria', 'titulo', 'conteudo', 'imagem_capa', 'nome_autor_externo', 'data_publicacao', 'publicado']
        
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Título da Postagem'}),
            'conteudo': EditorJsWidget(), 
            'imagem_capa': forms.FileInput(attrs={'class': 'form-control'}),
            'nome_autor_externo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: João (Trabalhador do Setor)'}),
            'data_publicacao': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'publicado': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'width: 20px; height: 20px;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.data_publicacao:
            self.fields['data_publicacao'].initial = self.instance.data_publicacao.strftime('%Y-%m-%dT%H:%M')