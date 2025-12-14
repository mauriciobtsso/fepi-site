from django.shortcuts import render, get_object_or_404, redirect
from .models import Livro, Categoria
from core.models import InformacaoContato
from django.db.models import Q
from django.utils.text import slugify
import re

def detalhe_livro(request, slug):
    # LÓGICA DE MIGRAÇÃO AUTOMÁTICA (Sem Shell)
    # Verifica se o 'slug' recebido é na verdade um número (ID antigo)
    if slug.isdigit():
        livro = get_object_or_404(Livro, pk=int(slug))
        # Se o livro ainda não tem slug, cria agora
        if not livro.slug:
            livro.slug = slugify(livro.titulo)
            livro.save()
        # Redireciona para a URL correta com o novo slug
        return redirect('detalhe_livro', slug=livro.slug)
    
    # Se não é número, busca pelo slug normalmente
    livro = get_object_or_404(Livro, slug=slug)
    
    contato = InformacaoContato.objects.first()
    
    whatsapp_num = ""
    whatsapp_msg = ""
    
    if contato and contato.telefone:
        nums = re.sub(r'\D', '', contato.telefone)
        whatsapp_num = f"55{nums}"
        # Prepara mensagem para URL
        whatsapp_msg = f"Olá, gostaria de adquirir o livro: *{livro.titulo}* (Cód: {livro.codigo})"

    return render(request, 'livraria/detalhe_livro.html', {
        'livro': livro, 
        'contato': contato,
        'whatsapp_num': whatsapp_num,
        'whatsapp_msg': whatsapp_msg
    })

def livraria_completa(request):
    query = request.GET.get('q')
    categoria_id = request.GET.get('cat') 
    
    livros = Livro.objects.all().order_by('titulo')

    if query:
        livros = livros.filter(Q(titulo__icontains=query) | Q(autor__icontains=query))
    
    if categoria_id:
        livros = livros.filter(categoria__id=categoria_id)

    categorias = Categoria.objects.all()
    contato = InformacaoContato.objects.first()

    contexto = {
        'livros': livros,
        'categorias': categorias,
        'busca_ativa': query,
        'cat_ativa': int(categoria_id) if categoria_id else None,
        'contato': contato
    }
    return render(request, 'livraria/livraria_completa.html', contexto)