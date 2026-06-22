# painel/forms/blogs.py
from django import forms
from django_editorjs_fields import EditorJsWidget
from blogs.models import PostBlog, BlogDepartamento, CategoriaBlog

class PostBlogForm(forms.ModelForm):
    class Meta:
        model = PostBlog
        fields = ['departamento', 'categoria', 'titulo', 'conteudo', 'imagem_capa', 'nome_autor_externo', 'data_publicacao', 'publicado']
        
        widgets = {
            'departamento': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            # Tentamos a inicialização padrão; se o erro persistir, 
            # o EditorJsWidget tentará ler a config do settings.py
            'conteudo': EditorJsWidget(), 
            'imagem_capa': forms.FileInput(attrs={'class': 'form-control'}),
            'nome_autor_externo': forms.TextInput(attrs={'class': 'form-control'}),
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


class ConfigBlogForm(forms.ModelForm):
    class Meta:
        model = BlogDepartamento
        fields = ['nome', 'cor_primaria', 'logo', 'descricao', 'instagram_url', 'instagram_widget_code']
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'cor_primaria': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/...'}),
            'instagram_widget_code': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Cole aqui o código embed...'}),
        }


class BlogDepartamentoCreateForm(forms.ModelForm):
    class Meta:
        model = BlogDepartamento
        fields = ['nome', 'subdominio', 'cor_primaria', 'logo', 'descricao', 'instagram_url', 'instagram_widget_code', 'ativo']
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Departamento de Infância e Juventude (DIJE)'}),
            'subdominio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: dije (Apenas letras minúsculas e sem espaço)'}),
            'cor_primaria': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/...'}),
            'instagram_widget_code': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Cole aqui o código embed...'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'width: 20px; height: 20px;'}),
        }


class CategoriaBlogForm(forms.ModelForm):
    class Meta:
        model = CategoriaBlog
        fields = ['nome', 'cor']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Eventos, Estudos, Comunicados'}),
            'cor': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
        }