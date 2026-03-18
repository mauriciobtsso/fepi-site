from django.shortcuts import render
from django.db.models import Q
from .models import Centro

def lista_centros(request):
    # 1. Pegar o termo que o usuário digitou na busca (se houver)
    query = request.GET.get('q')
    
    # 2. Preparar as listas base ordenadas
    centros_capital = Centro.objects.filter(tipo='CAPITAL').order_by('bairro', 'nome')
    centros_interior = Centro.objects.filter(tipo='INTERIOR').order_by('cidade', 'nome')
    especializadas = Centro.objects.filter(tipo='ESPECIALIZADA').order_by('nome')

    # 3. Se tiver busca, filtrar as listas
    if query:
        # Cria um filtro: Nome OU Endereço OU Bairro OU Cidade contém o texto digitado
        filtro_busca = (
            Q(nome__icontains=query) | 
            Q(endereco__icontains=query) | 
            Q(bairro__icontains=query) |
            Q(cidade__icontains=query)
        )
        
        centros_capital = centros_capital.filter(filtro_busca)
        centros_interior = centros_interior.filter(filtro_busca)
        especializadas = especializadas.filter(filtro_busca)

    contexto = {
        'capital': centros_capital,
        'interior': centros_interior,
        'especializadas': especializadas,
        'busca_ativa': query
    }
    return render(request, 'centros/lista_centros.html', contexto)