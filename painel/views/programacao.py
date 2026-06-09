# painel/views/programacao.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from programacao.models import AtividadeSemanal, Doutrinaria, CursoEvento
from painel.forms import AtividadeSemanalForm, DoutrinariaForm, CursoEventoForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def programacao_hub(request):
    return render(request, 'painel/programacao/programacao_hub.html')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_atividades(request):
    atividades = AtividadeSemanal.objects.all().order_by('dia', 'horario')
    return render(request, 'painel/programacao/listar_atividades.html', {'atividades': atividades})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_atividade(request, id=None):
    instancia = get_object_or_404(AtividadeSemanal, id=id) if id else None
    if request.method == 'POST':
        form = AtividadeSemanalForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('listar_atividades')
    else:
        form = AtividadeSemanalForm(instance=instancia)
    titulo = "Editar Atividade" if id else "Nova Atividade Semanal"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_atividade(request, id):
    item = get_object_or_404(AtividadeSemanal, id=id)
    item.delete()
    return redirect('listar_atividades')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_palestras(request):
    palestras = Doutrinaria.objects.all().order_by('-data_hora')
    return render(request, 'painel/programacao/listar_palestras.html', {'palestras': palestras})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_palestra(request, id=None):
    instancia = get_object_or_404(Doutrinaria, id=id) if id else None
    if request.method == 'POST':
        form = DoutrinariaForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('listar_palestras')
    else:
        form = DoutrinariaForm(instance=instancia)
    titulo = "Editar Palestra" if id else "Nova Palestra Pública"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_palestra(request, id):
    item = get_object_or_404(Doutrinaria, id=id)
    item.delete()
    return redirect('listar_palestras')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_eventos(request):
    eventos = CursoEvento.objects.all().order_by('-data_evento')
    return render(request, 'painel/programacao/listar_eventos.html', {'eventos': eventos})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_evento(request, id=None):
    instancia = get_object_or_404(CursoEvento, id=id) if id else None
    if request.method == 'POST':
        form = CursoEventoForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('listar_eventos')
    else:
        form = CursoEventoForm(instance=instancia)
    titulo = "Editar Evento Especial" if id else "Novo Curso ou Evento"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_evento(request, id):
    item = get_object_or_404(CursoEvento, id=id)
    item.delete()
    return redirect('listar_eventos')