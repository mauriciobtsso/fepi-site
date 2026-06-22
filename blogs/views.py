# blogs/views.py
from django.shortcuts import render, get_object_or_404
from .models import BlogDepartamento, PostBlog

def home_blog(request, subdominio):
    # Busca o departamento pelo nome do subdomínio (ex: 'dije')
    departamento = get_object_or_404(BlogDepartamento, subdominio=subdominio, ativo=True)
    
    # Pega apenas os posts publicados daquele departamento específico
    posts = departamento.posts.filter(publicado=True)
    
    contexto = {
        'departamento': departamento,
        'posts': posts
    }
    return render(request, 'blogs/home_blog.html', contexto)

def ler_post(request, subdominio, slug):
    # Valida o departamento
    departamento = get_object_or_404(BlogDepartamento, subdominio=subdominio, ativo=True)
    
    # Busca o post específico daquele departamento
    post = get_object_or_404(PostBlog, departamento=departamento, slug=slug, publicado=True)
    
    contexto = {
        'departamento': departamento,
        'post': post
    }
    return render(request, 'blogs/ler_post.html', contexto)