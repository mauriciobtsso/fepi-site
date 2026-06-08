from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from .models import Centro
import math
from decimal import Decimal

def calcular_distancia(lat1, lon1, lat2, lon2):
    """
    Calcula a distância entre dois pontos usando a fórmula de Haversine.
    Retorna a distância em quilômetros.
    """
    R = 6371  # Raio da Terra em km
    
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def lista_centros(request):
    query = request.GET.get('q', '')
    estado_req = request.GET.get('estado', '')
    cidade_req = request.GET.get('cidade', '')
    bairro_req = request.GET.get('bairro', '')
    user_lat = request.GET.get('user_lat', '').replace(',', '.')
    user_lon = request.GET.get('user_lon', '').replace(',', '.')
    raio_km = request.GET.get('raio', '50').replace(',', '.')  # Raio padrão de 50 km
    
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

    # Filtro por Proximidade (Geolocalização)
    centros_com_distancia = []
    if user_lat and user_lon:
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
            raio_km = float(raio_km)
            
            for centro in centros:
                if centro.latitude and centro.longitude:
                    distancia = calcular_distancia(
                        user_lat, user_lon,
                        float(centro.latitude), float(centro.longitude)
                    )
                    if distancia <= raio_km:
                        centro.distancia = round(distancia, 2)
                        centros_com_distancia.append(centro)
            
            # Ordena por distância
            centros_com_distancia.sort(key=lambda x: x.distancia)
            centros = centros_com_distancia
        except (ValueError, TypeError):
            pass

    # Pegar valores únicos para os dropdowns
    estados = Centro.objects.values_list('estado', flat=True).distinct().order_by('estado')
    cidades = Centro.objects.values_list('cidade', flat=True).distinct().order_by('cidade')
    bairros = Centro.objects.values_list('bairro', flat=True).distinct().order_by('bairro')

    # Dividir as listas para a visualização clássica
    if user_lat and user_lon:
        # Se geolocalização está ativa, não dividir por tipo
        centros_capital = []
        centros_interior = []
        especializadas = []
    else:
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
        
        # Variáveis de Geolocalização
        'user_lat': user_lat,
        'user_lon': user_lon,
        'raio_km': raio_km,
        'geolocation_ativa': bool(user_lat and user_lon),
    }
    return render(request, 'centros/lista_centros.html', contexto)

def api_centros_proximidade(request):
    """
    API para buscar centros próximos à localização do usuário.
    Retorna JSON com lista de centros ordenados por distância.
    """
    user_lat = request.GET.get('lat', '')
    user_lon = request.GET.get('lon', '')
    raio_km = request.GET.get('raio', '50')
    
    if not user_lat or not user_lon:
        return JsonResponse({'erro': 'Latitude e longitude são obrigatórias'}, status=400)
    
    try:
        user_lat = float(user_lat)
        user_lon = float(user_lon)
        raio_km = float(raio_km)
    except ValueError:
        return JsonResponse({'erro': 'Valores inválidos'}, status=400)
    
    centros = Centro.objects.filter(latitude__isnull=False, longitude__isnull=False)
    centros_proximidade = []
    
    for centro in centros:
        distancia = calcular_distancia(
            user_lat, user_lon,
            float(centro.latitude), float(centro.longitude)
        )
        if distancia <= raio_km:
            centros_proximidade.append({
                'id': centro.id,
                'nome': centro.nome,
                'endereco': centro.endereco,
                'numero': centro.numero or 'S/N',
                'bairro': centro.bairro,
                'cidade': centro.cidade,
                'estado': centro.estado,
                'latitude': float(centro.latitude),
                'longitude': float(centro.longitude),
                'telefone': centro.telefone or 'Não informado',
                'site': centro.site,
                'distancia': round(distancia, 2)
            })
    
    # Ordena por distância
    centros_proximidade.sort(key=lambda x: x['distancia'])
    
    return JsonResponse({
        'total': len(centros_proximidade),
        'centros': centros_proximidade
    })