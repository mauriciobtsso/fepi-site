# Importações Necessárias
from django.shortcuts import render, get_object_or_404  # <--- ADICIONEI get_object_or_404 AQUI
from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone
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
    # ANTES: palestras = Doutrinaria.objects.filter(data_hora__gte=hoje).order_by('data_hora')
    
    # AGORA: MOSTRA TUDO (PASSADO E FUTURO) PARA CONFIRMAR QUE EXISTE
    palestras = Doutrinaria.objects.all().order_by('data_hora')
    return render(request, 'programacao/doutrinarias.html', {'palestras': palestras})

def calendario(request):
    hoje = timezone.now()
    futuros = Doutrinaria.objects.filter(data_hora__gte=hoje).order_by('data_hora')
    passados = Doutrinaria.objects.filter(data_hora__lt=hoje).order_by('-data_hora')
    
    return render(request, 'programacao/calendario.html', {
        'futuros': futuros,
        'passados': passados
    })

def lista_cursos(request):
    hoje = timezone.now()
    futuros = CursoEvento.objects.filter(data_evento__gte=hoje).order_by('data_evento')
    passados = CursoEvento.objects.filter(data_evento__lt=hoje).order_by('-data_evento')
    
    return render(request, 'programacao/cursos.html', {'futuros': futuros, 'passados': passados})

def detalhe_curso(request, curso_id):
    # Agora esta linha vai funcionar porque importamos a função lá em cima
    curso = get_object_or_404(CursoEvento, pk=curso_id)
    return render(request, 'programacao/detalhe_curso.html', {'curso': curso})