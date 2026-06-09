# painel/views/doacoes.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from doacoes.models import FormaDoacao, PaginaDoacaoConfig
from painel.forms import FormaDoacaoForm, PaginaDoacaoConfigForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_doacoes(request):
    doacoes = FormaDoacao.objects.all().order_by('ordem')
    return render(request, 'painel/site/listar_doacoes.html', {'doacoes': doacoes})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_doacao(request, id=None):
    instancia = get_object_or_404(FormaDoacao, id=id) if id else None
    if request.method == 'POST':
        form = FormaDoacaoForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('listar_doacoes')
    else:
        form = FormaDoacaoForm(instance=instancia)
    titulo = "Editar Forma de Doação" if id else "Nova Forma de Doação"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_doacao(request, id):
    get_object_or_404(FormaDoacao, id=id).delete()
    return redirect('listar_doacoes')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def config_pagina_doacao(request):
    config, created = PaginaDoacaoConfig.objects.get_or_create(id=1)
    if request.method == 'POST':
        form = PaginaDoacaoConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Textos da página de doações atualizados!')
            return redirect('listar_doacoes')
    else:
        form = PaginaDoacaoConfigForm(instance=config)
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': 'Configurar Textos de Doação'})