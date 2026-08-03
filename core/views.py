from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from itertools import chain
from django.core.paginator import Paginator
from django.db.models import Q
from core.utils import enviar_email_sistema
from .models import ConfiguracaoEmail
from django.conf import settings
from django.core.cache import cache
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.vary import vary_on_headers
import requests
import xml.etree.ElementTree as ET

from core.models import Coluna
from .models import (
    ConfiguracaoHome, PostInstagram, InformacaoContato,
    PaginaInstitucional, MembroDiretoria, ConfiguracaoYouTube
)
from livraria.models import Livro, LivrariaConfig
from noticias.models import Noticia
from programacao.models import Doutrinaria, CursoEvento
from .forms import ContatoForm

def get_latest_youtube_video_id(channel_id):
    try:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'atom': 'http://www.w3.org/2005/Atom'}
            entry = root.find('atom:entry', ns)
            if entry:
                return entry.find('yt:videoId', ns).text
    except Exception as e:
        print(f"Erro YOUTUBE: {e}") 
    return None


@cache_page(60 * 15)
@vary_on_headers('Cookie')
def home(request):
    agora = timezone.now()

    ultimas_noticias = Noticia.objects.all().order_by('-data_publicacao')[:4]
    
    # Tratamento para SQLite Timezone no Home
    todos_cursos = CursoEvento.objects.all().order_by('data_evento')
    proximos_cursos = [c for c in todos_cursos if c.data_evento.replace(tzinfo=None) >= agora.replace(tzinfo=None)][:3]
    
    lista_carrossel = list(chain(ultimas_noticias, proximos_cursos))

    todas_palestras = Doutrinaria.objects.all().order_by('data_hora')
    palestras_agenda = [p for p in todas_palestras if p.data_hora.replace(tzinfo=None) >= agora.replace(tzinfo=None)]

    eventos_agenda_temp = sorted(
        chain(palestras_agenda, proximos_cursos),
        key=lambda evento: evento.data_hora if hasattr(evento, 'data_hora') else evento.data_evento
    )

    eventos_agenda = []
    for item in eventos_agenda_temp[:3]:
        if hasattr(item, 'tema'):
            item.tema = item.tema
            item.palestrante = item.palestrante
        else:
            item.tema = item.titulo
            item.palestrante = item.local
            item.data_hora = item.data_evento
        eventos_agenda.append(item)

    lista_livros = list(Livro.objects.filter(destaque_home=True).order_by('?')[:12])
    if len(lista_livros) < 12:
        faltam = 12 - len(lista_livros)
        extras = list(
            Livro.objects.exclude(id__in=[l.id for l in lista_livros])
            .order_by('-titulo')[:faltam]
        )
        lista_livros = lista_livros + extras

    config_home = ConfiguracaoHome.objects.first()
    contato = InformacaoContato.objects.first()
    livraria_config = LivrariaConfig.objects.first()
    posts_insta = PostInstagram.objects.all()[:4]
    colunas_home = Coluna.objects.filter(status='PUBLICADO').order_by('-data_publicacao')[:3]

    youtube_cfg = ConfiguracaoYouTube.objects.first()
    latest_video_id = None

    if youtube_cfg:
        mode = (youtube_cfg.youtube_mode or 'auto').strip()
        if mode == 'off':
            latest_video_id = None
        elif mode == 'fixed':
            latest_video_id = (youtube_cfg.youtube_video_id or "").strip() or None
        else:
            channel_id = (youtube_cfg.youtube_channel_id or "").strip()
            cache_key = f"fepi_yt_vid:{channel_id}"
            cached_vid = cache.get(cache_key)

            if cached_vid:
                 latest_video_id = cached_vid
            elif channel_id:
                latest_video_id = get_latest_youtube_video_id(channel_id)
                if latest_video_id:
                    cache.set(cache_key, latest_video_id, 60 * 15)

    contexto = {
        'carrossel': lista_carrossel,
        'noticias': ultimas_noticias,
        'agenda': eventos_agenda,
        'livros': lista_livros,
        'config': config_home,
        'contato': contato,
        'livraria_config': livraria_config,
        'instagram': posts_insta,
        'youtube_cfg': youtube_cfg,
        'youtube_video_id': latest_video_id,
        'colunas': colunas_home,
    }
    return render(request, 'core/index.html', contexto)


@never_cache
def institucional(request):
    pagina, _ = PaginaInstitucional.objects.get_or_create(pk=1, defaults={
        'titulo': 'Nossa História',
        'conteudo': '',
        'frase_destaque': '',
        'ano_inicio': 2024,
        'ano_fim': 2027
    })
    contato, _ = InformacaoContato.objects.get_or_create(pk=1)
    membros = MembroDiretoria.objects.all()

    executiva = membros.filter(tipo__nome__iexact='Diretoria Executiva').order_by('ordem')
    fiscal = membros.filter(tipo__nome__iexact='Conselho Fiscal').order_by('ordem')
    outros_departamentos = membros.exclude(
        Q(tipo__nome__iexact='Diretoria Executiva') | Q(tipo__nome__iexact='Conselho Fiscal')
    ).order_by('tipo__ordem', 'ordem')

    return render(request, 'core/institucional.html', {
        'pagina': pagina,
        'executiva': executiva,
        'fiscal': fiscal,
        'outros_departamentos': outros_departamentos,
        'contato': contato
    })


@never_cache
def fale_conosco(request):
    contato = InformacaoContato.objects.first()

    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            topico = form.cleaned_data['topico']
            nome = form.cleaned_data['nome']
            email_usuario = form.cleaned_data['email']
            mensagem = form.cleaned_data['mensagem']

            # Pega o "nome bonito" da escolha direto do formulário
            assunto_display = dict(form.fields['topico'].choices).get(topico, topico)

            subject = f"[{topico.upper()}] Novo Contato do Site - {nome}"
            
            # Define quem vai receber a mensagem (Diretoria FEPI)
            config_email = ConfiguracaoEmail.objects.first()
            if config_email and config_email.email_destino:
                destino = config_email.email_destino
            else:
                destino = getattr(settings, 'EMAIL_RECEIVER', 'contato@fepiaui.org.br')

            # Prepara os dados para o Template HTML do e-mail
            contexto_email = {
                'nome': nome,
                'email_usuario': email_usuario,
                'assunto_display': assunto_display,
                'mensagem': mensagem
            }

            try:
                # ---------------------------------------------------------
                # LÓGICA DINÂMICA DE E-MAIL (Usando template HTML + Brevo)
                # ---------------------------------------------------------
                enviar_email_sistema(
                    assunto=subject,
                    corpo="Este e-mail contém HTML. Por favor, visualize em um cliente compatível.", # Fallback para texto puro
                    destinatarios=[destino],
                    template_name='emails/contato_recebido.html', # Aponta para a nova pasta
                    context=contexto_email,
                    reply_to=email_usuario
                )
                
                return render(request, 'core/fale_conosco.html', {'contato': contato, 'sucesso': True})
            except Exception as e:
                print(f"ERRO DE EMAIL API: {e}")
                return render(request, 'core/fale_conosco.html', {'contato': contato, 'form': form, 'erro': True})
    else:
        form = ContatoForm()

    return render(request, 'core/fale_conosco.html', {'contato': contato, 'form': form})


@cache_page(60 * 60)
def privacidade(request):
    return render(request, 'core/privacidade.html', {'contato': InformacaoContato.objects.first()})


def listar_colunas_publicas(request):
    query = request.GET.get('q', '')
    colunas_list = Coluna.objects.filter(status='PUBLICADO').order_by('-data_publicacao')
    
    if query:
        colunas_list = colunas_list.filter(
            Q(titulo__icontains=query) | Q(resumo__icontains=query) |
            Q(nome_autor__icontains=query) | Q(autor_usuario__perfil__nome_razao_social__icontains=query)
        ).distinct()

    paginator = Paginator(colunas_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/colunas.html', {
        'colunas': page_obj,
        'query': query,
        'contato': InformacaoContato.objects.first()
    })

def detalhe_coluna(request, slug):
    coluna = get_object_or_404(Coluna, slug=slug, status='PUBLICADO')
    return render(request, 'core/detalhe_coluna.html', {
        'coluna': coluna,
        'contato': InformacaoContato.objects.first()
    })


# =========================================================
# VIEWS PÚBLICAS DE PROGRAMAÇÃO E NOTÍCIAS (COM PAGINAÇÃO)
# =========================================================

def doutrinarias(request):
    """ Exibe as palestras. O Python organiza as futuras e passadas numa lista única para evitar bugs no Aiven. """
    agora = timezone.now()
    # Garante que a data atual esteja no mesmo formato "ingênuo" do banco para não dar erro
    agora_naive = make_naive(agora) if is_aware(agora) else agora
    
    todas_palestras = Doutrinaria.objects.all()
    
    futuras = []
    passadas = []
    
    for p in todas_palestras:
        if p.data_hora:
            p_data_naive = make_naive(p.data_hora) if is_aware(p.data_hora) else p.data_hora
            if p_data_naive >= agora_naive:
                p.is_past = False  # Etiqueta para o HTML
                futuras.append(p)
            else:
                p.is_past = True   # Etiqueta para o HTML
                passadas.append(p)
                
    # Ordena as futuras da mais próxima para a mais distante (Crescente)
    futuras.sort(key=lambda x: x.data_hora)
    
    # Ordena as passadas da mais recente para a mais velha (Decrescente)
    passadas.sort(key=lambda x: x.data_hora, reverse=True)
    
    # Junta tudo em uma lista só (O HTML antigo já lê isso!)
    lista_final = futuras + passadas

    # Paginação para não pesar a tela
    paginator = Paginator(lista_final, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/doutrinarias.html', {
        'palestras': page_obj,
        'contato': InformacaoContato.objects.first()
    })

def lista_cursos(request):
    """ Exibe os cursos e eventos com a mesma blindagem de fuso horário """
    agora = timezone.now().replace(tzinfo=None)
    
    todos_cursos = CursoEvento.objects.all().order_by('data_evento')
    
    futuras_list = []
    passadas_list = []
    
    for curso in todos_cursos:
        if curso.data_evento:
            data_limpa = curso.data_evento.replace(tzinfo=None)
            if data_limpa >= agora:
                futuras_list.append(curso)
            else:
                passadas_list.append(curso)
                
    passadas_list.reverse()
    
    paginator = Paginator(passadas_list, 6)
    page_number = request.GET.get('page')
    passadas_paginadas = paginator.get_page(page_number)
    
    return render(request, 'core/cursos.html', {
        'futuras': futuras_list,
        'passadas': passadas_paginadas,
        'contato': InformacaoContato.objects.first()
    })

def lista_noticias(request):
    noticias_list = Noticia.objects.all().order_by('-data_publicacao')
    
    paginator = Paginator(noticias_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/lista_noticias.html', {
        'noticias': page_obj,
        'contato': InformacaoContato.objects.first()
    })