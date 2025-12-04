from django.shortcuts import render
from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone # <--- Importante
from .models import AtividadeSemanal, Doutrinaria

def atividades(request):
    # Ordenação dos dias da semana
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
    # Mostra apenas as futuras para a lista de "Próximas"
    hoje = timezone.now()
    palestras = Doutrinaria.objects.filter(data_hora__gte=hoje).order_by('data_hora')
    return render(request, 'programacao/doutrinarias.html', {'palestras': palestras})

def calendario(request):
    hoje = timezone.now()
    
    # Lista 1: Futuros (Ordenado por data crescente: mais próximo primeiro)
    futuros = Doutrinaria.objects.filter(data_hora__gte=hoje).order_by('data_hora')
    
    # Lista 2: Passados (Ordenado por data decrescente: mais recente primeiro)
    passados = Doutrinaria.objects.filter(data_hora__lt=hoje).order_by('-data_hora')
    
    return render(request, 'programacao/calendario.html', {
        'futuros': futuros,
        'passados': passados
    })