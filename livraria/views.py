from django.shortcuts import render, get_object_or_404, redirect
from .models import Livro, Categoria, LivrariaConfig
from django.http import JsonResponse
from core.models import InformacaoContato
from .models import ProdutoLivraria
from django.db.models import Q
from django.utils.text import slugify
import re

def detalhe_livro(request, slug):
    # LÓGICA DE MIGRAÇÃO AUTOMÁTICA (Legado)
    if slug.isdigit():
        livro = get_object_or_404(Livro, pk=int(slug))
        if not livro.slug:
            livro.slug = slugify(livro.titulo)
            livro.save()
        return redirect('detalhe_livro', slug=livro.slug)
    
    # Busca o livro pelo Slug
    livro = get_object_or_404(Livro, slug=slug)
    
    # 1. Busca as configurações da Livraria (WhatsApp, Logo, etc)
    config = LivrariaConfig.objects.first()
    
    whatsapp_num = ""
    whatsapp_msg = ""
    
    # 2. Se existir configuração e tiver número de WhatsApp salvo
    if config and config.whatsapp:
        # Remove qualquer caractere que não seja número (espaço, traço, parênteses)
        whatsapp_num = re.sub(r'\D', '', config.whatsapp)
        
        # Prepara a mensagem padrão
        whatsapp_msg = f"Olá, gostaria de adquirir o livro: *{livro.titulo}* (Cód: {livro.codigo})"

    return render(request, 'livraria/detalhe_livro.html', {
        'livro': livro, 
        'config': config,         # Passamos a config para exibir logo ou instagram se precisar
        'whatsapp_num': whatsapp_num,
        'whatsapp_msg': whatsapp_msg
    })

def livraria_completa(request):
    query = request.GET.get('q')
    categoria_id = request.GET.get('cat') 
    
    # A vitrine mostra apenas livros ativados; a consulta de acervo usa ProdutoLivraria e permanece independente.
    livros = Livro.objects.filter(ativo_na_vitrine=True).order_by('titulo')

    # Filtros
    if query:
        livros = livros.filter(Q(titulo__icontains=query) | Q(autor__icontains=query))
    
    if categoria_id:
        livros = livros.filter(categoria__id=categoria_id)

    categorias = Categoria.objects.all()
    
    # Busca configurações (para exibir Logo e Instagram no topo da página)
    config = LivrariaConfig.objects.first()

    contexto = {
        'livros': livros,
        'categorias': categorias,
        'busca_ativa': query,
        'cat_ativa': int(categoria_id) if categoria_id else None,
        'config': config # Agora o template usa 'config.logo' e 'config.instagram_url'
    }
    return render(request, 'livraria/livraria_completa.html', contexto)

def consulta_rapida_page(request):
    """Renderiza a página pública de consulta da livraria"""
    return render(request, 'livraria/consulta_estoque.html')

def api_buscar_produtos(request):
    """API instantânea para buscar produtos sem recarregar a página"""
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'error': 'Digite um código de barras ou nome do produto.'}, status=400)
    
    # Busca exata no código ou busca flexível no nome (limite de 15 para não pesar a tela)
    produtos = ProdutoLivraria.objects.filter(
        Q(codigo_barras=query) | Q(descricao__icontains=query)
    ).order_by('descricao')[:15]
    
    if not produtos.exists():
        return JsonResponse({'error': 'Nenhum produto encontrado em nossa base de dados.'}, status=404)
        
    dados = []
    for p in produtos:
        dados.append({
            'codigo_barras': p.codigo_barras,
            'descricao': p.descricao,
            'preco_venda': float(p.preco_venda) if p.preco_venda else 0.0,
            'quantidade_estoque': p.quantidade_estoque,
            'editora': p.editora if p.editora else 'Não informada'
        })
    return JsonResponse({'produtos': dados})