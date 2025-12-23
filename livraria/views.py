from django.shortcuts import render, get_object_or_404, redirect
from .models import Livro, Categoria, LivrariaConfig
from core.models import InformacaoContato
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
    
    livros = Livro.objects.all().order_by('titulo')

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