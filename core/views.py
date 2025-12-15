from django.shortcuts import render
from django.utils import timezone
from itertools import chain
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
import requests
import xml.etree.ElementTree as ET

from .models import (
    ConfiguracaoHome, PostInstagram, InformacaoContato,
    PaginaInstitucional, MembroDiretoria, ConfiguracaoYouTube
)
from livraria.models import Livro, LivrariaConfig
from noticias.models import Noticia
from programacao.models import Doutrinaria, CursoEvento
from .forms import ContatoForm

# Função auxiliar interna (para não depender de outros arquivos)
def get_latest_youtube_video_id(channel_id):
    try:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        
        # O SEGREDO: Adicionar um User-Agent para simular um navegador real
        # Sem isso, o YouTube bloqueia requisições vindas de servidores (como o Railway)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            # Namespaces do XML do YouTube
            ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'atom': 'http://www.w3.org/2005/Atom'}
            entry = root.find('atom:entry', ns)
            if entry:
                video_id = entry.find('yt:videoId', ns).text
                return video_id
        else:
            print(f"Erro YouTube: Status {response.status_code}")
            
    except Exception as e:
        print(f"Erro ao buscar YouTube: {e}")
        
    return None


def home(request):
    agora = timezone.now()

    # 1. CARROSSEL
    ultimas_noticias = Noticia.objects.all().order_by('-data_publicacao')[:4]
    proximos_cursos = CursoEvento.objects.filter(data_evento__gte=agora).order_by('data_evento')[:3]
    lista_carrossel = list(chain(ultimas_noticias, proximos_cursos))

    # 2. AGENDA
    palestras_agenda = Doutrinaria.objects.filter(data_hora__gte=agora)
    cursos_agenda = CursoEvento.objects.filter(data_evento__gte=agora)

    eventos_agenda_temp = sorted(
        chain(palestras_agenda, cursos_agenda),
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

    # 3. LIVROS
    lista_livros = list(Livro.objects.filter(destaque_home=True).order_by('?')[:12])
    if len(lista_livros) < 12:
        faltam = 12 - len(lista_livros)
        extras = list(
            Livro.objects.exclude(id__in=[l.id for l in lista_livros])
            .order_by('-titulo')[:faltam]
        )
        lista_livros = lista_livros + extras

    # 4. CONFIGURAÇÕES
    config_home = ConfiguracaoHome.objects.first()
    contato = InformacaoContato.objects.first()
    livraria_config = LivrariaConfig.objects.first()
    posts_insta = PostInstagram.objects.all()[:4]

    # 5. YOUTUBE
    youtube_cfg = ConfiguracaoYouTube.objects.first()
    latest_video_id = None

    if youtube_cfg:
        mode = (youtube_cfg.youtube_mode or 'auto').strip()

        if mode == 'off':
            latest_video_id = None

        elif mode == 'fixed':
            fixed_id = (youtube_cfg.youtube_video_id or "").strip()
            latest_video_id = fixed_id or None

        else: # modo auto
            channel_id = (youtube_cfg.youtube_channel_id or "").strip()
            cache_key = f"fepi_latest_youtube_video_id:{channel_id or 'no_channel'}"
            latest_video_id = cache.get(cache_key)

            if not latest_video_id and channel_id:
                latest_video_id = get_latest_youtube_video_id(channel_id)
                # Salva no cache por 30 min se encontrou
                if latest_video_id:
                    cache.set(cache_key, latest_video_id, 60 * 30)

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
        'youtube_video_id': latest_video_id, # Usar este nome no template
    }
    return render(request, 'core/index.html', contexto)


def institucional(request):
    pagina = PaginaInstitucional.objects.first()
    contato = InformacaoContato.objects.first()
    membros = MembroDiretoria.objects.all()

    executiva = membros.filter(tipo__nome='Diretoria Executiva').order_by('ordem')
    fiscal = membros.filter(tipo__nome='Conselho Fiscal').order_by('ordem')

    outros_departamentos = membros.exclude(
        Q(tipo__nome='Diretoria Executiva') | Q(tipo__nome='Conselho Fiscal')
    ).order_by('tipo__ordem', 'ordem')

    contexto = {
        'pagina': pagina,
        'executiva': executiva,
        'fiscal': fiscal,
        'outros_departamentos': outros_departamentos,
        'contato': contato
    }
    return render(request, 'core/institucional.html', contexto)


def fale_conosco(request):
    contato = InformacaoContato.objects.first()

    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            topico = form.cleaned_data['topico']
            nome = form.cleaned_data['nome']
            email = form.cleaned_data['email']
            mensagem = form.cleaned_data['mensagem']

            subject = f"[{topico.upper()}] Novo Contato do Site - {nome}"
            body = (
                f"Mensagem de: {nome}\n"
                f"Email: {email}\n"
                f"Assunto: {form.get_topico_display(topico)}\n\n"
                f"--- Mensagem ---\n{mensagem}"
            )

            try:
                send_mail(
                    subject, body, settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_RECEIVER], fail_silently=False
                )
                return render(request, 'core/fale_conosco.html', {'contato': contato, 'sucesso': True})
            except Exception as e:
                print(f"ERRO DE EMAIL: {e}")
                return render(request, 'core/fale_conosco.html', {'contato': contato, 'form': form, 'erro': True})
    else:
        form = ContatoForm()

    return render(request, 'core/fale_conosco.html', {'contato': contato, 'form': form})


def privacidade(request):
    contato = InformacaoContato.objects.first()
    return render(request, 'core/privacidade.html', {'contato': contato})