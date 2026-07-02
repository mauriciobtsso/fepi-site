import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='instagram_embed')
def instagram_embed(text):
    """
    Substitui uma marcação [ig: URL] por um iframe leve do Instagram.
    """
    if not text:
        return ""

    # Padrão para encontrar a tag [ig: LINK_DO_INSTAGRAM]
    pattern = r'\[ig:\s*(https?://(?:www\.)?instagram\.com/(?:p|reel)/[a-zA-Z0-9_-]+).*?\]'

    def replace_with_iframe(match):
        url = match.group(1)
        # Garante que a URL termine com barra para o embed funcionar
        if not url.endswith('/'):
            url += '/'
        embed_url = f"{url}embed/"
        
        # Retorna um iframe responsivo, leve e sem depender de scripts externos pesados
        return (
            f'<div style="display: flex; justify-content: center; margin: 20px 0;">'
            f'<iframe src="{embed_url}" width="400" height="480" frameborder="0" '
            f'scrolling="no" allowtransparency="true" '
            f'style="border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"></iframe>'
            f'</div>'
        )

    # Substitui a tag pelo iframe e marca como seguro para renderizar HTML
    formatted_text = re.sub(pattern, replace_with_iframe, text)
    return mark_safe(formatted_text)