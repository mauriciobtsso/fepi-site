from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Noticia

def lista_noticias(request):
    query = request.GET.get('q', '')
    noticias_list = Noticia.objects.all().order_by('-data_publicacao')
    
    if query:
        noticias_list = noticias_list.filter(
            Q(titulo__icontains=query) |
            Q(resumo__icontains=query) |
            Q(conteudo__icontains=query) |
            Q(autor__icontains=query)
        )
    
    # Contagem total de resultados (antes de paginar)
    total_resultados = noticias_list.count()
    
    # Configuração da Paginação (10 notícias por página)
    paginator = Paginator(noticias_list, 10)
    page = request.GET.get('page')
    
    try:
        noticias = paginator.page(page)
    except PageNotAnInteger:
        # Se a página não for um inteiro, entrega a primeira página
        noticias = paginator.page(1)
    except EmptyPage:
        # Se a página estiver fora do alcance, entrega a última página de resultados
        noticias = paginator.page(paginator.num_pages)
    
    return render(request, 'noticias/lista_noticias.html', {
        'noticias': noticias,
        'query': query,
        'total_resultados': total_resultados
    })

def detalhe_noticia(request, slug):
    noticia = get_object_or_404(Noticia, slug=slug)
    ultimas_noticias = Noticia.objects.exclude(slug=slug).order_by('-data_publicacao')[:3]

    return render(request, 'noticias/detalhe_noticia.html', {
        'noticia': noticia,
        'ultimas_noticias': ultimas_noticias
    })