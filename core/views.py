from django.shortcuts import render
from django.utils import timezone
from itertools import chain 
from .models import ConfiguracaoHome, PostInstagram, InformacaoContato, PaginaInstitucional, MembroDiretoria
from livraria.models import Livro
from noticias.models import Noticia
from programacao.models import Doutrinaria, CursoEvento

def home(request):
    agora = timezone.now()

    # 1. CARROSSEL
    ultimas_noticias = Noticia.objects.all().order_by('-data_publicacao')[:4]
    proximos_cursos = CursoEvento.objects.filter(data_evento__gte=agora).order_by('data_evento')[:3]
    lista_carrossel = list(chain(ultimas_noticias, proximos_cursos))

    # 2. Agenda
    lista_agenda = Doutrinaria.objects.filter(data_hora__gte=agora).order_by('data_hora')[:3]
    
    # 3. LIVROS (ALTERADO AQUI!)
    # order_by('?') embaralha a lista. [:4] pega os 4 primeiros sorteados.
    lista_livros = Livro.objects.all().order_by('?')[:4]
    
    # 4. Configurações
    config_home = ConfiguracaoHome.objects.first()
    contato = InformacaoContato.objects.first()
    posts_insta = PostInstagram.objects.all()[:4]
    
    contexto = {
        'carrossel': lista_carrossel,
        'noticias': ultimas_noticias,
        'agenda': lista_agenda,
        'livros': lista_livros,
        'config': config_home,
        'contato': contato,
        'instagram': posts_insta
    }
    return render(request, 'core/index.html', contexto)

def institucional(request):
    pagina = PaginaInstitucional.objects.first()
    executiva = MembroDiretoria.objects.filter(tipo='EXECUTIVA').order_by('ordem')
    fiscal = MembroDiretoria.objects.filter(tipo='FISCAL').order_by('ordem')
    contato = InformacaoContato.objects.first()
    
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