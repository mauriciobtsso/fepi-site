from django.shortcuts import render
from django.db.models import Prefetch 
from .models import SecaoLink, LinkItem

def links_uteis(request):
    # Busca seções que têm links úteis (is_download=False)
    secoes = SecaoLink.objects.filter(
        linkitem__is_download=False
    ).prefetch_related(
        Prefetch('linkitem_set', queryset=LinkItem.objects.filter(is_download=False))
    ).distinct().order_by('ordem')
    
    return render(request, 'recursos/links_uteis.html', {'secoes': secoes})

def downloads(request):
    # ALTERADO: Agora busca SEÇÕES que têm downloads (is_download=True)
    # Isso permite agrupar os downloads por categoria no template
    secoes = SecaoLink.objects.filter(
        linkitem__is_download=True
    ).prefetch_related(
        Prefetch('linkitem_set', queryset=LinkItem.objects.filter(is_download=True))
    ).distinct().order_by('ordem')
    
    return render(request, 'recursos/downloads.html', {'secoes': secoes})