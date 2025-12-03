from django.shortcuts import render
from livraria.models import Livro
from noticias.models import Noticia

def home(request):
    # Pega os 4 primeiros livros e as 3 últimas notícias
    lista_livros = Livro.objects.all()[:4]
    lista_noticias = Noticia.objects.all()[:3]
    
    contexto = {
        'livros': lista_livros,
        'noticias': lista_noticias
    }
    return render(request, 'core/index.html', contexto)

# --- ESTA É A FUNÇÃO QUE ESTAVA FALTANDO ---
def institucional(request):
    return render(request, 'core/institucional.html')