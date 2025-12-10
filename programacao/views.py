# programacao/views.py

from django.shortcuts import render, get_object_or_404
from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone
from django.utils.formats import date_format # <-- IMPORTANTE: Para o mês em PT-BR
from itertools import chain, groupby 
from operator import attrgetter 
from .models import AtividadeSemanal, Doutrinaria, CursoEvento


def atividades(request):
    atividades = AtividadeSemanal.objects.annotate(
        ordem_dia=Case(
            When(dia='SEG', then=Value(1)),
            When(dia='TER', then=Value(2)),
            When(dia='QUA', then=Value(3)),
            When(dia='QUI', then=Value(4)),
            When(dia='SEX', then=Value(5)),
            When(dia='SAB', then=Value(6)),
            When(dia='DOM', then=Value(7)),
            output_field=IntegerField(),
        )
    ).order_by('ordem_dia', 'horario')
    
    return render(request, 'programacao/atividades.html', {'atividades': atividades})

def doutrinarias(request):
    palestras = Doutrinaria.objects.all().order_by('-data_hora')
    return render(request, 'programacao/doutrinarias.html', {'palestras': palestras})

def calendario(request):
    agora = timezone.now()
    
    # 1. BUSCA EVENTOS
    palestras_futuras = Doutrinaria.objects.filter(data_hora__gte=agora)
    cursos_futuros = CursoEvento.objects.filter(data_evento__gte=agora)
    
    # 2. PREPARA LISTA FUTURA
    eventos_futuros = []
    for evento in chain(palestras_futuras, cursos_futuros):
        # Normaliza campos
        if hasattr(evento, 'data_hora'):
            evento.sort_date = evento.data_hora
            evento.is_palestra = True
        else:
            evento.sort_date = evento.data_evento
            evento.is_palestra = False
        
        # Cria a chave de grupo JÁ TRADUZIDA (Ex: "Dezembro 2025")
        evento.group_key = date_format(evento.sort_date, "F Y") 
        eventos_futuros.append(evento)

    # Ordena e Agrupa
    eventos_futuros.sort(key=attrgetter('sort_date'))
    # groupby exige que a lista esteja ordenada pela chave que vamos agrupar
    grupos_futuros = [{'mes_ano': key, 'list': list(group)} for key, group in groupby(eventos_futuros, attrgetter('group_key'))]


    # 3. PREPARA LISTA PASSADA
    palestras_passadas = Doutrinaria.objects.filter(data_hora__lt=agora)
    cursos_passados = CursoEvento.objects.filter(data_evento__lt=agora)
    
    eventos_passados = []
    for evento in chain(palestras_passadas, cursos_passados):
        if hasattr(evento, 'data_hora'):
            evento.sort_date = evento.data_hora
            evento.is_palestra = True
        else:
            evento.sort_date = evento.data_evento
            evento.is_palestra = False
        
        # Chave traduzida
        evento.group_key = date_format(evento.sort_date, "F Y")
        eventos_passados.append(evento)
    
    # Ordena decrescente
    eventos_passados.sort(key=attrgetter('sort_date'), reverse=True)
    grupos_passados = [{'mes_ano': key, 'list': list(group)} for key, group in groupby(eventos_passados, attrgetter('group_key'))]

    return render(request, 'programacao/calendario.html', {
        'futuros': grupos_futuros, 
        'passados': grupos_passados 
    })

def lista_cursos(request):
    hoje = timezone.now()
    futuros = CursoEvento.objects.filter(data_evento__gte=hoje).order_by('data_evento')
    passados = CursoEvento.objects.filter(data_evento__lt=hoje).order_by('-data_evento')
    
    return render(request, 'programacao/cursos.html', {'futuros': futuros, 'passados': passados})

def detalhe_curso(request, curso_id):
    curso = get_object_or_404(CursoEvento, pk=curso_id)
    return render(request, 'programacao/detalhe_curso.html', {'curso': curso})