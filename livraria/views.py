from django.shortcuts import render, get_object_or_404
from .models import Livro

# ... (se houver código anterior, mantém ou adiciona abaixo)

def detalhe_livro(request, livro_id):
    # O get_object_or_404 é ótimo: se o usuário tentar inventar um ID que não existe, dá erro 404 automaticamente
    livro = get_object_or_404(Livro, pk=livro_id)
    
    return render(request, 'livraria/detalhe_livro.html', {'livro': livro})