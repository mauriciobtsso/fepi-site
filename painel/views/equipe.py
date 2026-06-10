# painel/views/equipe.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import Cargo, TipoDiretoria, MembroDiretoria
from painel.forms import CargoForm, TipoDiretoriaForm, MembroDiretoriaForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def equipe_hub(request):
    membros = MembroDiretoria.objects.all().order_by('tipo__ordem', 'ordem')
    departamentos = TipoDiretoria.objects.all().order_by('ordem')
    cargos = Cargo.objects.all().order_by('nome')
    return render(request, 'painel/secretaria/equipe_hub.html', {
        'membros': membros,
        'departamentos': departamentos,
        'cargos': cargos
    })

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_membro(request, id=None):
    instancia = get_object_or_404(MembroDiretoria, id=id) if id else None
    if request.method == 'POST':
        form = MembroDiretoriaForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('equipe_hub')
    else:
        form = MembroDiretoriaForm(instance=instancia)
    titulo = "Editar Membro" if id else "Novo Membro da Diretoria"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_membro(request, id):
    get_object_or_404(MembroDiretoria, id=id).delete()
    return redirect('equipe_hub')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_departamento(request, id=None):
    instancia = get_object_or_404(TipoDiretoria, id=id) if id else None
    if request.method == 'POST':
        form = TipoDiretoriaForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('equipe_hub')
    else:
        form = TipoDiretoriaForm(instance=instancia)
    titulo = "Editar Departamento" if id else "Novo Departamento"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_departamento(request, id):
    get_object_or_404(TipoDiretoria, id=id).delete()
    return redirect('equipe_hub')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_cargo(request, id=None):
    instancia = get_object_or_404(Cargo, id=id) if id else None
    if request.method == 'POST':
        form = CargoForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('equipe_hub')
    else:
        form = CargoForm(instance=instancia)
    titulo = "Editar Cargo" if id else "Novo Cargo"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_cargo(request, id):
    cargo = get_object_or_404(Cargo, id=id)
    if not cargo.membrodiretoria_set.exists():
        cargo.delete()
    return redirect('equipe_hub')