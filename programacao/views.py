from django.shortcuts import render
from django.db.models import Case, When, Value, IntegerField
from .models import AtividadeSemanal, Doutrinaria

def atividades(request):
    # Aqui criamos uma "coluna invisível" (ordem_dia) com números de 1 a 7
    # para forçar o banco a obedecer a nossa ordem: Segunda a Domingo.
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
    ).order_by('ordem_dia', 'horario') # Ordena pelo número do dia e depois pelo horário
    
    return render(request, 'programacao/atividades.html', {'atividades': atividades})

def doutrinarias(request):
    palestras = Doutrinaria.objects.all().order_by('data_hora')
    return render(request, 'programacao/doutrinarias.html', {'palestras': palestras})

def calendario(request):
    eventos = Doutrinaria.objects.all().order_by('data_hora')
    return render(request, 'programacao/calendario.html', {'eventos': eventos})