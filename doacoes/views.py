from django.shortcuts import render
from .models import FormaDoacao, PaginaDoacaoConfig

def doacoes_view(request):
    # Cria a config caso não exista nenhuma salva ainda
    config, created = PaginaDoacaoConfig.objects.get_or_create(id=1)
    formas = FormaDoacao.objects.all()
    
    return render(request, 'doacoes/doacoes.html', {
        'config': config,
        'formas': formas
    })