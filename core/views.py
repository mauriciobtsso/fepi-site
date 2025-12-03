from django.shortcuts import render
from livraria.models import Livro
from noticias.models import Noticia  # <--- Importamos o novo modelo

def home(request):
    # Pega os 4 primeiros livros
    lista_livros = Livro.objects.all()[:4]
    
    # Pega as 3 últimas notícias (o 'ordering' no model já garante que são as novas)
    lista_noticias = Noticia.objects.all()[:3]
    
    contexto = {
        'livros': lista_livros,
        'noticias': lista_noticias # <--- Enviamos para o HTML
    }
    
    return render(request, 'core/index.html', contexto)