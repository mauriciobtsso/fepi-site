from django.shortcuts import render, get_object_or_404
from .models import Noticia

def lista_noticias(request):
    noticias = Noticia.objects.all().order_by('-data_publicacao')
    return render(request, 'noticias/lista_noticias.html', {'noticias': noticias})

# MUDANÇA AQUI: Recebe 'slug' em vez de 'noticia_id'
def detalhe_noticia(request, slug):
    # Busca pelo campo slug
    noticia = get_object_or_404(Noticia, slug=slug)
    
    # Pegamos as 3 últimas notícias (exceto a atual) para a sidebar
    ultimas_noticias = Noticia.objects.exclude(slug=slug).order_by('-data_publicacao')[:3]

    return render(request, 'noticias/detalhe_noticia.html', {
        'noticia': noticia,
        'ultimas_noticias': ultimas_noticias
    })