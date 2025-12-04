from django.shortcuts import render
from django.db.models import Prefetch # Permite otimizar a busca
from .models import SecaoLink, LinkItem

def links_uteis(request):
    # Busca apenas as seções que contêm links (is_download=False)
    secoes = SecaoLink.objects.filter(
        linkitem__is_download=False
    ).prefetch_related(
        Prefetch('linkitem_set', queryset=LinkItem.objects.filter(is_download=False))
    ).distinct().order_by('ordem')
    
    return render(request, 'recursos/links_uteis.html', {'secoes': secoes})

def downloads(request):
    # Busca todos os itens marcados como download
    downloads = LinkItem.objects.filter(is_download=True).order_by('-id')
    return render(request, 'recursos/downloads.html', {'downloads': downloads})