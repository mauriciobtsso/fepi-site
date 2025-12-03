from django.shortcuts import render
# Importamos o modelo de Livro que criaste na outra app
from livraria.models import Livro 

def home(request):
    # Pedimos ao banco de dados: "Dá-me todos os livros"
    # O [:4] no final significa "Pega apenas os 4 primeiros" (para não lotar a home)
    lista_livros = Livro.objects.all()[:4]
    
    # Criamos um "contexto" (um pacote de dados para enviar ao HTML)
    contexto = {
        'livros': lista_livros
    }
    
    # Enviamos o contexto junto com o HTML
    return render(request, 'core/index.html', contexto)