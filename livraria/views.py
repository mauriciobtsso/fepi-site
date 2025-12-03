from django.shortcuts import render, get_object_or_404
from .models import Livro

def detalhe_livro(request, livro_id):
    # Busca o livro pelo ID ou dá erro 404 se não existir
    livro = get_object_or_404(Livro, pk=livro_id)
    
    return render(request, 'livraria/detalhe_livro.html', {'livro': livro})