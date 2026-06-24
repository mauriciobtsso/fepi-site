# painel/views/recursos.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator
from recursos.models import SecaoLink, LinkItem
from painel.forms import SecaoLinkForm, LinkItemForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def recursos_hub(request):
    query = request.GET.get('q', '')
    secao_id = request.GET.get('secao', '')
    
    # Busca base de itens
    itens_list = LinkItem.objects.select_related('secao').all().order_by('secao__ordem', 'titulo')
    
    # Filtros
    if query:
        itens_list = itens_list.filter(Q(titulo__icontains=query) | Q(url__icontains=query))
    if secao_id:
        itens_list = itens_list.filter(secao_id=secao_id)
        
    # Paginação
    paginator = Paginator(itens_list, 15)
    page_number = request.GET.get('page')
    itens = paginator.get_page(page_number)
    
    secoes = SecaoLink.objects.all().order_by('ordem')
    
    return render(request, 'painel/site/recursos_hub.html', {
        'secoes': secoes,
        'itens': itens,
        'query': query,
        'secao_id': secao_id
    })

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