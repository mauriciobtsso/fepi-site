"""
core/templatetags/cloudinary_tags.py

Filtro para aplicar transformações automáticas em URLs do Cloudinary.

USO NO TEMPLATE:
    {% load cloudinary_tags %}
    <img src="{{ item.imagem.url|cloudinary_transform:'w_815,h_455,c_fill,f_auto,q_auto' }}">

INSTALAÇÃO:
    1. Crie a pasta: core/templatetags/  (se não existir)
    2. Crie o arquivo: core/templatetags/__init__.py  (vazio)
    3. Salve este arquivo como: core/templatetags/cloudinary_tags.py
"""

from django import template

register = template.Library()


@register.filter
def cloudinary_transform(url, transformations):
    """
    Insere transformações na URL do Cloudinary.
    
    Exemplo:
        {{ imagem.url|cloudinary_transform:'w_400,h_400,c_fill,f_auto,q_auto' }}
    
    Transforma:
        https://res.cloudinary.com/xxx/image/upload/v1/media/foto.jpg
    Em:
        https://res.cloudinary.com/xxx/image/upload/w_400,h_400,c_fill,f_auto,q_auto/v1/media/foto.jpg
    """
    if not url or 'cloudinary' not in url:
        return url
    
    # Evita aplicar duas vezes
    if transformations in url:
        return url
    
    return url.replace('/upload/', f'/upload/{transformations}/', 1)