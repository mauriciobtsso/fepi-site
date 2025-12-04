from django.shortcuts import render
from django.utils import timezone # Para pegar a data de hoje
from livraria.models import Livro
from noticias.models import Noticia
from programacao.models import Doutrinaria
from .models import ConfiguracaoHome, PostInstagram, InformacaoContato, PaginaInstitucional, MembroDiretoria

def home(request):
    # 1. Notícias (Pega as 3 últimas)
    lista_noticias = Noticia.objects.all()[:3]
    
    # 2. Agenda (Pega as próximas 3 palestras a partir de hoje)
    agora = timezone.now()
    lista_agenda = Doutrinaria.objects.filter(data_hora__gte=agora).order_by('data_hora')[:3]
    
    # 3. Configurações Gerais (Banner, YouTube, Contato)
    config_home = ConfiguracaoHome.objects.first()
    contato = InformacaoContato.objects.first()
    
    # 4. Instagram (Opcional, caso queira usar no futuro)
    posts_insta = PostInstagram.objects.all()[:4]
    
    contexto = {
        'noticias': lista_noticias,
        'agenda': lista_agenda,
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

def livraria_completa(request):
    livros = Livro.objects.all()
    contato = InformacaoContato.objects.first()
    return render(request, 'livraria/livraria_completa.html', {'livros': livros, 'contato': contato})