import json
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
