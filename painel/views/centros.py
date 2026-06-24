# painel/views/centros.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator
from centros.models import Centro
from painel.forms import CentroForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_centros(request):
    query = request.GET.get('q', '')
    cidade_filtro = request.GET.get('cidade', '')
    
    centros_list = Centro.objects.all().order_by('cidade', 'nome')
    
    # Filtro de Busca por nome
    if query:
        centros_list = centros_list.filter(Q(nome__icontains=query))
    
    # Filtro por cidade
    if cidade_filtro:
        centros_list = centros_list.filter(cidade=cidade_filtro)
    
    # Paginação
    paginator = Paginator(centros_list, 15)
    page_number = request.GET.get('page')
    centros = paginator.get_page(page_number)
    
    # Lista de cidades distintas para o filtro
    cidades = Centro.objects.values_list('cidade', flat=True).distinct().order_by('cidade')
    
    return render(request, 'painel/secretaria/listar_centros.html', {
        'centros': centros,
        'query': query,
        'cidade_filtro': cidade_filtro,
        'cidades': cidades
    })

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_centro(request, id=None):
    instancia = get_object_or_404(Centro, id=id) if id else None
    if request.method == 'POST':
        form = CentroForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('listar_centros')
    else:
        form = CentroForm(instance=instancia)
    titulo = "Editar Centro Espírita" if id else "Novo Centro Espírita"
    return render(request, 'painel/secretaria/form_centro.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_centro(request, id):
    get_object_or_404(Centro, id=id).delete()
    return redirect('listar_centros')