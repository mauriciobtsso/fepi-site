from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Noticia

def lista_noticias(request):
    query = request.GET.get('q', '')
    noticias = Noticia.objects.all().order_by('-data_publicacao')
    
    if query:
        noticias = noticias.filter(
            Q(titulo__icontains=query) |
            Q(resumo__icontains=query) |
            Q(conteudo__icontains=query) |
            Q(autor__icontains=query)
        )
    
    return render(request, 'noticias/lista_noticias.html', {
        'noticias': noticias,
        'query': query,
        'total_resultados': noticias.count()
    })

def detalhe_noticia(request, slug):
    noticia = get_object_or_404(Noticia, slug=slug)
    ultimas_noticias = Noticia.objects.exclude(slug=slug).order_by('-data_publicacao')[:3]

    return render(request, 'noticias/detalhe_noticia.html', {
        'noticia': noticia,
        'ultimas_noticias': ultimas_noticias
    })