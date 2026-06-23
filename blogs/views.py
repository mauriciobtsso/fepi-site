# blogs/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogDepartamento, PostBlog, CategoriaBlog

def home_blog(request, subdominio=None):
    # 🚀 SOLUÇÃO: Pega o "dije" direto da URL (ex: dije.fepiaui.org.br)
    if not subdominio:
        subdominio = request.get_host().split('.')[0]

    departamento = get_object_or_404(BlogDepartamento, subdominio=subdominio, ativo=True)
    posts_list = PostBlog.objects.filter(departamento=departamento, publicado=True).order_by('-data_publicacao')
    
    # 1. Filtro por Pesquisa de Texto
    query = request.GET.get('q', '')
    if query:
        posts_list = posts_list.filter(Q(titulo__icontains=query) | Q(resumo__icontains=query))
        
    # 2. Filtro por Categoria
    categoria_slug = request.GET.get('categoria', '')
    categoria_atual = None
    if categoria_slug:
        categoria_atual = CategoriaBlog.objects.filter(slug=categoria_slug).first()
        if categoria_atual:
            posts_list = posts_list.filter(categoria=categoria_atual)
        
    # Paginação
    paginator = Paginator(posts_list, 9)
    page_number = request.GET.get('page')
    posts_paginados = paginator.get_page(page_number)

    contexto = {
        'departamento': departamento,
        'posts': posts_paginados,
        'query': query,
        'categoria_atual': categoria_atual, 
    }
    return render(request, 'blogs/home_blog.html', contexto)


def ler_post(request, slug, subdominio=None):
    # 🚀 SOLUÇÃO: Mesma trava de segurança para a leitura dos posts
    if not subdominio:
        subdominio = request.get_host().split('.')[0]
        
    # Valida o departamento
    departamento = get_object_or_404(BlogDepartamento, subdominio=subdominio, ativo=True)
    
    # Busca o post específico
    post = get_object_or_404(PostBlog, departamento=departamento, slug=slug, publicado=True)
    
    contexto = {
        'departamento': departamento,
        'post': post
    }
    return render(request, 'blogs/ler_post.html', contexto)