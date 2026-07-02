import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='embed_media')
def embed_media(text):
    """
    Substitui as marcações [ig: URL] e [yt: URL] por iframes leves 
    do Instagram e do YouTube, respectivamente.
    """
    if not text:
        return ""

    # ==========================================
    # 1. PROCESSAMENTO DO INSTAGRAM
    # ==========================================
    ig_pattern = r'\[ig:\s*(https?://(?:www\.)?instagram\.com/(?:p|reel)/[a-zA-Z0-9_-]+).*?\]'
    
    def replace_ig(match):
        url = match.group(1)
        # Garante que a URL termine com barra para o embed funcionar
        if not url.endswith('/'):
            url += '/'
        embed_url = f"{url}embed/"
        
        return (
            f'<div style="display: flex; justify-content: center; margin: 20px 0;">'
            f'<iframe src="{embed_url}" width="400" height="480" frameborder="0" '
            f'scrolling="no" allowtransparency="true" '
            f'style="border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"></iframe>'
            f'</div>'
        )

    # Aplica a substituição do Instagram
    text = re.sub(ig_pattern, replace_ig, text)

    # ==========================================
    # 2. PROCESSAMENTO DO YOUTUBE
    # ==========================================
    # Pega tanto links "youtube.com/watch?v=ID" quanto "youtu.be/ID"
    yt_pattern = r'\[yt:\s*https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+).*?\]'
    
    def replace_yt(match):
        video_id = match.group(1)
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        
        return (
            f'<div style="display: flex; justify-content: center; margin: 20px 0;">'
            f'<iframe width="560" height="315" src="{embed_url}" frameborder="0" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
            f'allowfullscreen style="border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"></iframe>'
            f'</div>'
        )

    # Aplica a substituição do YouTube
    text = re.sub(yt_pattern, replace_yt, text)

    # Retorna o texto formatado e seguro para o HTML
    return mark_safe(text)