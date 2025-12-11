from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import DocumentoRestrito

@login_required
def area_federado(request):
    busca = request.GET.get('q', '')
    filtro_categoria = request.GET.get('categoria', '')
    
    # Definição das categorias para o menu de filtros
    todas_categorias = DocumentoRestrito.CATEGORIAS

    # MODO 1: PESQUISA OU FILTRO ATIVO (Lista Plana)
    if busca or filtro_categoria:
        modo_exibicao = 'lista'
        documentos = DocumentoRestrito.objects.all()
        
        if busca:
            documentos = documentos.filter(
                Q(titulo__icontains=busca) | Q(descricao__icontains=busca)
            )
        if filtro_categoria:
            documentos = documentos.filter(categoria=filtro_categoria)
            
        conteudo = {'documentos': documentos}

    # MODO 2: DASHBOARD PADRÃO (Agrupado por Categoria)
    else:
        modo_exibicao = 'agrupado'
        grupos = []
        
        # Para cada categoria definida no Model, buscamos os documentos
        for codigo, nome in todas_categorias:
            docs = DocumentoRestrito.objects.filter(categoria=codigo)
            if docs.exists():
                grupos.append({
                    'titulo_categoria': nome,
                    'codigo': codigo,
                    'lista': docs
                })
        
        conteudo = {'grupos': grupos}

    context = {
        'modo_exibicao': modo_exibicao,
        'categorias': todas_categorias,
        'busca_atual': busca,
        'categoria_atual': filtro_categoria,
        'user': request.user,
    }
    context.update(conteudo)
    
    return render(request, 'intranet/dashboard.html', context)