# core/views.py

from django.shortcuts import render, redirect
from django.utils import timezone
from itertools import chain
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache

from .models import (
    ConfiguracaoHome, PostInstagram, InformacaoContato,
    PaginaInstitucional, MembroDiretoria
)
from livraria.models import Livro, LivrariaConfig
from noticias.models import Noticia
from programacao.models import Doutrinaria, CursoEvento
from .forms import ContatoForm

# ✅ Import do util do YouTube
from core.utils.youtube import get_latest_youtube_video_id


def home(request):
    agora = timezone.now()

    # 1. CARROSSEL
    ultimas_noticias = Noticia.objects.all().order_by('-data_publicacao')[:4]
    proximos_cursos = CursoEvento.objects.filter(data_evento__gte=agora).order_by('data_evento')[:3]
    lista_carrossel = list(chain(ultimas_noticias, proximos_cursos))

    # 2. Agenda
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
    lista_livros = Livro.objects.filter(destaque_home=True).order_by('?')[:12]
    if not lista_livros.exists():
        lista_livros = Livro.objects.all().order_by('-titulo')[:12]

    # 4. Configurações
    config_home = ConfiguracaoHome.objects.first()
    contato = InformacaoContato.objects.first()
    livraria_config = LivrariaConfig.objects.first()
    posts_insta = PostInstagram.objects.all()[:4]

    # ✅ 5. Último vídeo do YouTube (automático, com cache)
    cache_key = "fepi_latest_youtube_video_id"
    latest_video_id = cache.get(cache_key)

    if not latest_video_id:
        try:
            latest_video_id = get_latest_youtube_video_id()
            # guarda por 30 min (ajuste se quiser)
            cache.set(cache_key, latest_video_id, 60 * 30)
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
        'latest_video_id': latest_video_id,  # ✅ novo
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
