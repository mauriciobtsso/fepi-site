from django.shortcuts import render
from django.utils import timezone
from itertools import chain 
from .models import ConfiguracaoHome, PostInstagram, InformacaoContato, PaginaInstitucional, MembroDiretoria
from livraria.models import Livro, LivrariaConfig
from noticias.models import Noticia
from programacao.models import Doutrinaria, CursoEvento
from django.db.models import Q

def home(request):
    agora = timezone.now()

    # 1. CARROSSEL
    ultimas_noticias = Noticia.objects.all().order_by('-data_publicacao')[:4]
    proximos_cursos = CursoEvento.objects.filter(data_evento__gte=agora).order_by('data_evento')[:3]
    lista_carrossel = list(chain(ultimas_noticias, proximos_cursos))

    # 2. Agenda
    lista_agenda = Doutrinaria.objects.filter(data_hora__gte=agora).order_by('data_hora')[:3]
    
    # 3. LIVROS (Lógica de Segurança)
    # Tenta pegar 4 destaques aleatórios
    lista_livros = Livro.objects.filter(destaque_home=True).order_by('?')[:4]
    
    # Se não houver nenhum livro marcado como destaque, mostra os 4 últimos para a seção não ficar vazia.
    if not lista_livros.exists():
        lista_livros = Livro.objects.all().order_by('-titulo')[:4] 
    
    # 4. Configurações
    config_home = ConfiguracaoHome.objects.first()
    contato = InformacaoContato.objects.first()
    livraria_config = LivrariaConfig.objects.first() 
    posts_insta = PostInstagram.objects.all()[:4]
    
    contexto = {
        'carrossel': lista_carrossel,
        'noticias': ultimas_noticias,
        'agenda': lista_agenda,
        'livros': lista_livros,
        'config': config_home,
        'contato': contato,
        'livraria_config': livraria_config,
        'instagram': posts_insta
    }
    return render(request, 'core/index.html', contexto)

def institucional(request):
    # OBTEM DADOS
    pagina = PaginaInstitucional.objects.first()
    contato = InformacaoContato.objects.first()
    
    # NOVAS BUSCAS: Membros por Tipo (CORRIGIDO AQUI!)
    membros = MembroDiretoria.objects.all()
    
    # 1. Diretoria Executiva: Filtramos pelo CAMPO 'nome' na tabela relacionada (tipo__nome)
    executiva = membros.filter(tipo__nome='Diretoria Executiva').order_by('ordem')
    
    # 2. Conselho Fiscal
    fiscal = membros.filter(tipo__nome='Conselho Fiscal').order_by('ordem')
    
    # 3. Departamentos
    outros_departamentos = membros.exclude(
        Q(tipo__nome='Diretoria Executiva') | Q(tipo__nome='Conselho Fiscal')
    ).order_by('tipo__ordem', 'ordem')
    
    # Agrupamento para o Template
    membros_departamentos = []
    if outros_departamentos.exists():
        from django.template import Context 
        membros_departamentos = regroup(outros_departamentos, 'tipo')


    contexto = {
        'pagina': pagina,
        'executiva': executiva,
        'fiscal': fiscal,
        'membros_departamentos': membros_departamentos,
        'contato': contato
    }
    return render(request, 'core/institucional.html', contexto)

def fale_conosco(request):
    contato = InformacaoContato.objects.first()
    return render(request, 'core/fale_conosco.html', {'contato': contato})