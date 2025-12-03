from django.shortcuts import render
from .models import Centro

def lista_centros(request):
    # Separamos as listas para mostrar em abas ou secções diferentes
    centros_capital = Centro.objects.filter(tipo='CAPITAL').order_by('nome')
    centros_interior = Centro.objects.filter(tipo='INTERIOR').order_by('cidade', 'nome')
    especializadas = Centro.objects.filter(tipo='ESPECIALIZADA').order_by('nome')

    contexto = {
        'capital': centros_capital,
        'interior': centros_interior,
        'especializadas': especializadas
    }
    return render(request, 'centros/lista_centros.html', contexto)