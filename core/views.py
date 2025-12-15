# core/views.py

from django.shortcuts import render
from django.utils import timezone
from itertools import chain
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache

from .models import (
    ConfiguracaoHome, PostInstagram, InformacaoContato,
    PaginaInstitucional, MembroDiretoria, ConfiguracaoYouTube
)
from livraria.models import Livro, LivrariaConfig
from noticias.models import Noticia
from programacao.models import Doutrinaria, CursoEvento
from .forms import ContatoForm

from core.utils.youtube import get_latest_youtube_video_id


def home(request):
    agora = timezone.now()

    # 1. CARROSSEL
    ultimas_noticias = Noticia.objects.all().order_by('-data_publicacao')[:4]
    proximos_cursos = CursoEvento.objects.filter(data_evento__gte=agora).order_by('data_evento')[:3]
    lista_carrossel = list(chain(ultimas_noticias, proximos_cursos))

    # 2. AGENDA (3 próximos eventos, unificando tipos)
    palestras_agenda = Doutrinaria.objects.filter(data_hora__gte=agora)
    cursos_agenda = CursoEvento.objects.filter(data_evento__gte=agora)

    eventos_agenda_temp = sorted(
        chain(palestras_agenda, cursos_agenda),
        key=lambda evento: evento.data_hora if hasattr(evento, 'data_hora') else evento.data_evento
    )

    eventos_agenda = []
    for item in eventos_agenda_temp[:3]:
        if hasattr(item, 'tema'):
            # Doutrinaria
            item.tema = item.tema
            item.palestrante = item.palestrante
        else:
            # CursoEvento
            item.tema = item.titulo
            item.palestrante = item.local
            item.data_hora = item.data_evento
        eventos_agenda.append(item)

    # 3. LIVROS (12, preenchendo com fallback)
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

    # 5. YOUTUBE (modo AUTO/FIXED/OFF via ConfiguracaoYouTube + cache)
    youtube_cfg = ConfiguracaoYouTube.objects.first()
    latest_video_id = None

    if youtube_cfg:
        mode = (youtube_cfg.youtube_mode or 'auto').strip()

        if mode == 'off':
            latest_video_id = None

        elif mode == 'fixed':
            fixed_id = (youtube_cfg.youtube_video_id or "").strip()
            latest_video_id = fixed_id or None

        else:
            channel_id = (youtube_cfg.youtube_channel_id or "").strip()
            cache_key = f"fepi_latest_youtube_video_id:{channel_id or 'no_channel'}"
            latest_video_id = cache.get(cache_key)

            if not latest_video_id and channel_id:
                try:
                    latest_video_id = get_latest_youtube_video_id(channel_id)
                    cache.set(cache_key, latest_video_id, 60 * 30)  # 30 min
                except Exception:
                    latest_video_id = None

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
        'latest_video_id': latest_video_id,
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
