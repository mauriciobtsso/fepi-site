# painel/views/colunas.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.text import slugify
from django.utils import timezone
from core.models import Coluna
from painel.forms import ColunaForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_colunas(request):
    colunas = Coluna.objects.all().order_by('-data_publicacao')
    return render(request, 'painel/colunas/listar_colunas.html', {'colunas': colunas})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def criar_coluna(request):
    if request.method == 'POST':
        form = ColunaForm(request.POST, request.FILES)
        if form.is_valid():
            coluna = form.save(commit=False)
            if not coluna.slug:
                coluna.slug = slugify(coluna.titulo)
            coluna.save()
            messages.success(request, "Artigo criado com sucesso!")
            return redirect('listar_colunas')
    else:
        form = ColunaForm(initial={'data_publicacao': timezone.now()})
    return render(request, 'painel/colunas/criar_coluna.html', {'form': form, 'titulo': 'Escrever Artigo'})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def editar_coluna(request, id):
    coluna = get_object_or_404(Coluna, id=id)
    if request.method == 'POST':
        form = ColunaForm(request.POST, request.FILES, instance=coluna)
        if form.is_valid():
            form.save()
            messages.success(request, "Artigo atualizado!")
            return redirect('listar_colunas')
    else:
        form = ColunaForm(instance=coluna)
    return render(request, 'painel/colunas/criar_coluna.html', {'form': form, 'titulo': 'Editar Artigo'})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_coluna(request, id):
    coluna = get_object_or_404(Coluna, id=id)
    coluna.delete()
    messages.success(request, "Artigo excluído.")
    return redirect('listar_colunas')