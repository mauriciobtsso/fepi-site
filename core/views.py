from django.shortcuts import render, get_object_or_404
from django.utils import timezone # Para pegar a data de hoje
from livraria.models import Livro, Categoria
from django.db.models import Q 
from noticias.models import Noticia
from core.models import InformacaoContato
from programacao.models import Doutrinaria
from .models import ConfiguracaoHome, PostInstagram, InformacaoContato, PaginaInstitucional, MembroDiretoria
import re

def home(request):
    # 1. Notícias (Pega as 3 últimas)
    lista_noticias = Noticia.objects.all()[:3]
    
    # 2. Agenda (Pega as próximas 3 palestras a partir de hoje)
    agora = timezone.now()
    lista_agenda = Doutrinaria.objects.filter(data_hora__gte=agora).order_by('data_hora')[:3]
    
    # 3. Livros (Pega os 2 primeiros para destaque na home) <--- ESTA LINHA FALTAVA
    lista_livros = Livro.objects.all()[:2]
    
    # 4. Configurações Gerais
    config_home = ConfiguracaoHome.objects.first()
    contato = InformacaoContato.objects.first()
    
    # 5. Instagram
    posts_insta = PostInstagram.objects.all()[:4]
    
    contexto = {
        'noticias': lista_noticias,
        'agenda': lista_agenda,
        'livros': lista_livros,  # <--- ADICIONADO AO CONTEXTO
        'config': config_home,
        'contato': contato,
        'instagram': posts_insta
    }
    return render(request, 'core/index.html', contexto)

def institucional(request):
    pagina = PaginaInstitucional.objects.first()
    executiva = MembroDiretoria.objects.filter(tipo='EXECUTIVA').order_by('ordem')
    fiscal = MembroDiretoria.objects.filter(tipo='FISCAL').order_by('ordem')
    contato = InformacaoContato.objects.first() # Para o rodapé
    
    contexto = {
        'pagina': pagina,
        'executiva': executiva,
        'fiscal': fiscal,
        'contato': contato
    }
    return render(request, 'core/institucional.html', contexto)

def fale_conosco(request):
    contato = InformacaoContato.objects.first()
    return render(request, 'core/fale_conosco.html', {'contato': contato})

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

    # CORREÇÃO AQUI: Buscamos as categorias no banco, não mais na lista fixa
    categorias = Categoria.objects.all()
    
    contato = InformacaoContato.objects.first()

    contexto = {
        'livros': livros,
        'categorias': categorias,
        'busca_ativa': query,
        # Converte para int para comparar no template, se existir
        'cat_ativa': int(categoria_id) if categoria_id else None,
        'contato': contato
    }
    return render(request, 'livraria/livraria_completa.html', contexto)