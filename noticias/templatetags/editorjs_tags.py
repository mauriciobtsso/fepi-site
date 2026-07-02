import json
import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='to_editorjs')
def to_editorjs(value):
    """
    Converte o valor do campo EditorJsJSONField para um dicionário Python,
    garantindo que o template consiga iterar sobre 'blocks'.
    """
    if not value:
        return None

    # Se já for um dicionário (JSONField nativo)
    if isinstance(value, dict):
        return value

    # Se for uma string (TextField ou JSONField que retornou string)
    if isinstance(value, str):
        try:
            # Limpeza básica para evitar erros com strings vazias ou 'null'
            clean_value = value.strip()
            if clean_value in ['', 'null', 'None', '{}']:
                return None
            return json.loads(clean_value)
        except (json.JSONDecodeError, TypeError):
            return None

    # Se for um objeto da biblioteca (algumas versões retornam um wrapper)
    if hasattr(value, 'data'):
        return value.data

    return None


@register.filter(name='embed_media')
def embed_media(text):
    """
    Processa textos e converte marcações ou links diretos do Instagram e YouTube
    em iframes responsivos. Agora com proteção para garantir entrada de string.
    """
    # Garantir que o texto seja uma string, caso contrário, retorna vazio
    if text is None:
        return ""
    
    # Se o valor for um objeto que não é string, converte para string
    if not isinstance(text, str):
        text = str(text)

    # ==========================================
    # 1. PROCESSAMENTO DO INSTAGRAM
    # ==========================================
    ig_pattern = r'(?:\[ig:\s*)?(https?://(?:www\.)?instagram\.com/(?:p|reel)/([a-zA-Z0-9_-]+))[/?]?[^\s\]]*\]?'

    def replace_ig(match):
        video_id = match.group(2)
        embed_url = f"https://www.instagram.com/reel/{video_id}/embed/"
        
        return (
            f'<div style="display: flex; justify-content: center; margin: 20px 0;">'
            f'<iframe src="{embed_url}" width="400" height="480" frameborder="0" '
            f'scrolling="no" allowtransparency="true" '
            f'style="border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"></iframe>'
            f'</div>'
        )

    text = re.sub(ig_pattern, replace_ig, text)

    # ==========================================
    # 2. PROCESSAMENTO DO YOUTUBE
    # ==========================================
    yt_pattern = r'(?:\[yt:\s*)?(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+))[^\s\]]*\]?'
    
    def replace_yt(match):
        video_id = match.group(2)
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        
        return (
            f'<div style="display: flex; justify-content: center; margin: 20px 0;">'
            f'<iframe width="560" height="315" src="{embed_url}" frameborder="0" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
            f'allowfullscreen style="border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"></iframe>'
            f'</div>'
        )

    text = re.sub(yt_pattern, replace_yt, text)

    return mark_safe(text)