from django.shortcuts import render, get_object_or_404
from .models import Noticia

def detalhe_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, pk=noticia_id)
    return render(request, 'noticias/detalhe_noticia.html', {'noticia': noticia})

def lista_noticias(request):
    noticias = Noticia.objects.all().order_by('-data_publicacao')
    return render(request, 'noticias/lista_noticias.html', {'noticias': noticias})