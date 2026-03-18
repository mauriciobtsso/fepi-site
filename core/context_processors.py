# core/context_processors.py

from django.utils import timezone
from .models import InformacaoContato, ConfiguracaoHome # <-- Importante: ConfiguracaoHome
from livraria.models import LivrariaConfig

def site_wide_context(request):
    """
    Injeta dados globais (Contato, Configurações, Pop-up) em todas as páginas.
    """
    
    # 1. Busca os Singletons
    contato = InformacaoContato.objects.first()
    livraria_config = LivrariaConfig.objects.first()
    config_home = ConfiguracaoHome.objects.first()
    
    # 2. Lógica do Pop-up
    popup_valido = None
    
    if config_home and config_home.popup_ativo:
        agora = timezone.now()
        
        # Verifica se a data atual está dentro do período configurado
        # Se popup_inicio/fim forem nulos (erro de cadastro), ignoramos para não quebrar
        if config_home.popup_inicio and config_home.popup_fim:
            if config_home.popup_inicio <= agora <= config_home.popup_fim:
                popup_valido = config_home
        else:
            # Se não tiver datas configuradas mas estiver ativo, mostra sempre (ou ajuste conforme preferir)
            popup_valido = config_home

    return {
        'contato': contato,
        'livraria_config': livraria_config,
        'config_home': config_home, # Útil para banner/youtube
        'popup_ativo': popup_valido, # A variável mágica que o base.html espera!
    }