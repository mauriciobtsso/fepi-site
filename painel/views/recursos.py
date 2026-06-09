# painel/views/recursos.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from recursos.models import SecaoLink, LinkItem
from painel.forms import SecaoLinkForm, LinkItemForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def recursos_hub(request):
    secoes = SecaoLink.objects.all().order_by('ordem')
    itens = LinkItem.objects.all().select_related('secao').order_by('secao__ordem', 'titulo')
    return render(request, 'painel/site/recursos_hub.html', {'secoes': secoes, 'itens': itens})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_recurso(request, id=None):
    instancia = get_object_or_404(LinkItem, id=id) if id else None
    if request.method == 'POST':
        form = LinkItemForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('recursos_hub')
    else:
        form = LinkItemForm(instance=instancia)
    titulo = "Editar Recurso/Link" if id else "Novo Recurso/Link"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_recurso(request, id):
    get_object_or_404(LinkItem, id=id).delete()
    return redirect('recursos_hub')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_secao_recurso(request, id=None):
    instancia = get_object_or_404(SecaoLink, id=id) if id else None
    if request.method == 'POST':
        form = SecaoLinkForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('recursos_hub')
    else:
        form = SecaoLinkForm(instance=instancia)
    titulo = "Editar Seção de Recursos" if id else "Nova Seção"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_secao_recurso(request, id):
    secao = get_object_or_404(SecaoLink, id=id)
    secao.delete()
    return redirect('recursos_hub')