from django.shortcuts import render, get_object_or_404
from .models import Livro, Categoria  # <--- Importante: Importar Categoria
from core.models import InformacaoContato
from django.db.models import Q 
import re

def detalhe_livro(request, livro_id):
    livro = get_object_or_404(Livro, pk=livro_id)
    contato = InformacaoContato.objects.first()
    
    whatsapp_num = ""
    whatsapp_msg = ""
    
    if contato and contato.telefone:
        nums = re.sub(r'\D', '', contato.telefone)
        whatsapp_num = f"55{nums}"
        whatsapp_msg = f"Olá, gostaria de adquirir o livro: *{livro.titulo}* (Cód: {livro.codigo})"

    return render(request, 'livraria/detalhe_livro.html', {
        'livro': livro, 
        'contato': contato,
        'whatsapp_num': whatsapp_num,
        'whatsapp_msg': whatsapp_msg
    })

def livraria_completa(request):
    query = request.GET.get('q')
    categoria_id = request.GET.get('cat') # Recebe o ID da categoria
    
    livros = Livro.objects.all().order_by('titulo')

    # Filtro de Busca (Texto)
    if query:
        livros = livros.filter(Q(titulo__icontains=query) | Q(autor__icontains=query))
    
    # Filtro de Categoria (Banco de Dados)
    if categoria_id:
        livros = livros.filter(categoria__id=categoria_id)

    # --- A CORREÇÃO ESTÁ AQUI ---
    # Antes estava: categorias = Livro.CATEGORIAS (Isso causava o erro)
    # Agora buscamos no banco:
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