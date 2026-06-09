# painel/views/centros.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from centros.models import Centro
from painel.forms import CentroForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_centros(request):
    centros = Centro.objects.all().order_by('cidade', 'nome')
    return render(request, 'painel/secretaria/listar_centros.html', {'centros': centros})

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