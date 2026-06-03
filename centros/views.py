from django.shortcuts import render
from django.db.models import Q
from .models import Centro

def lista_centros(request):
    query = request.GET.get('q', '')
    estado_req = request.GET.get('estado', '')
    cidade_req = request.GET.get('cidade', '')
    bairro_req = request.GET.get('bairro', '')
    
    centros = Centro.objects.all().order_by('nome')

    # Filtros Dinâmicos
    if query:
        centros = centros.filter(Q(nome__icontains=query) | Q(endereco__icontains=query))
    if estado_req:
        centros = centros.filter(estado=estado_req)
    if cidade_req:
        centros = centros.filter(cidade=cidade_req)
    if bairro_req:
        centros = centros.filter(bairro=bairro_req)

    # Pegar valores únicos para os dropdowns
    estados = Centro.objects.values_list('estado', flat=True).distinct().order_by('estado')
    cidades = Centro.objects.values_list('cidade', flat=True).distinct().order_by('cidade')
    bairros = Centro.objects.values_list('bairro', flat=True).distinct().order_by('bairro')

    # Dividir as listas para a visualização clássica
    centros_capital = centros.filter(tipo='CAPITAL').order_by('bairro', 'nome')
    centros_interior = centros.filter(tipo='INTERIOR').order_by('cidade', 'nome')
    especializadas = centros.filter(tipo='ESPECIALIZADA').order_by('nome')

    contexto = {
        'centros': centros, # Lista completa para o mapa renderizar
        'capital': centros_capital,
        'interior': centros_interior,
        'especializadas': especializadas,
        
        # Variáveis de Filtro
        'busca_ativa': query,
        'estado_req': estado_req,
        'cidade_req': cidade_req,
        'bairro_req': bairro_req,
        'estados': estados,
        'cidades': cidades,
        'bairros': bairros,
    }
    return render(request, 'centros/lista_centros.html', contexto)