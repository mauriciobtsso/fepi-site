from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import DocumentoRestrito, CategoriaDocumento

@login_required(login_url='/login/')
def area_federado(request):
    # --- 1. Preparação dos Dados Básicos ---
    # Buscamos todas as categorias para montar o menu de filtros
    todas_categorias = CategoriaDocumento.objects.all()
    
    # Queryset base de documentos (trazendo junto a categoria para otimizar banco)
    base_docs = DocumentoRestrito.objects.select_related('categoria').order_by('-data_publicacao')

    # --- 2. Captura dos Filtros da URL ---
    busca_atual = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria')

    # Convertendo ID da categoria para Inteiro (se existir)
    try:
        if categoria_id:
            categoria_id = int(categoria_id)
        else:
            categoria_id = None
    except ValueError:
        categoria_id = None

    # --- 3. Decisão do Modo de Exibição ---
    
    # CENÁRIO A: Se tem busca ou filtro ativo -> MODO LISTA (Resultados planos)
    if busca_atual or categoria_id:
        modo_exibicao = 'lista'
        grupos = None # Não vamos usar grupos aqui

        # Aplica Filtro de Categoria
        if categoria_id:
            base_docs = base_docs.filter(categoria__id=categoria_id)

        # Aplica Filtro de Texto (Título ou Descrição)
        if busca_atual:
            base_docs = base_docs.filter(
                Q(titulo__icontains=busca_atual) | 
                Q(descricao__icontains=busca_atual)
            )
        
        # A variável 'documentos' vai para o template com a lista filtrada
        documentos_finais = base_docs

    # CENÁRIO B: Sem filtros (Dashboard Inicial) -> MODO AGRUPADO
    else:
        modo_exibicao = 'agrupado'
        documentos_finais = None # Não vamos usar lista plana aqui
        grupos = []

        # Para cada categoria existente no banco...
        for cat in todas_categorias:
            # ...pegamos os documentos dela
            docs_da_categoria = base_docs.filter(categoria=cat)
            
            # Se tiver documento, adicionamos ao grupo para exibir
            if docs_da_categoria.exists():
                grupos.append({
                    'titulo_categoria': cat.nome,
                    'lista': docs_da_categoria
                })

    # --- 4. Renderização Final ---
    return render(request, 'intranet/dashboard.html', {
        'user': request.user,
        'modo_exibicao': modo_exibicao,
        'categorias': todas_categorias,     # Para o menu de botões (pills)
        'documentos': documentos_finais,    # Usado se modo == 'lista'
        'grupos': grupos,                   # Usado se modo == 'agrupado'
        'busca_atual': busca_atual,
        'categoria_atual': categoria_id,
    })