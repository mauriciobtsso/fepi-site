# core/context_processors.py

from .models import InformacaoContato # Puxa o modelo de contato
from livraria.models import LivrariaConfig # Puxa a configuração da Livraria

def site_wide_context(request):
    """
    Injeta o objeto de Contato (para cabeçalho e rodapé) 
    em TODAS as páginas do site automaticamente.
    """
    
    contato = InformacaoContato.objects.first()
    livraria_config = LivrariaConfig.objects.first()
    
    return {
        'contato': contato,
        'livraria_config': livraria_config,
    }