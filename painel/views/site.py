# painel/views/site.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import ConfiguracaoHome, ConfiguracaoYouTube, PostInstagram, PaginaInstitucional
from painel.forms import PopupForm, YoutubeConfigForm, PostInstagramForm, PaginaInstitucionalForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def site_hub(request):
    return render(request, 'painel/site/site_hub.html')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_popup(request):
    config = ConfiguracaoHome.objects.first()
    if not config:
        config = ConfiguracaoHome.objects.create()
    if request.method == 'POST':
        form = PopupForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            return redirect('painel_home')
    else:
        form = PopupForm(instance=config)
    return render(request, 'painel/gerenciar_popup.html', {'form': form})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def config_youtube(request):
    config, created = ConfiguracaoYouTube.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = YoutubeConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            return redirect('site_hub')
    else:
        form = YoutubeConfigForm(instance=config)
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': 'Destaque do YouTube'})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_instagram(request):
    posts = PostInstagram.objects.all().order_by('-data_post')
    return render(request, 'painel/site/listar_instagram.html', {'posts': posts})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_post_insta(request, id=None):
    post = get_object_or_404(PostInstagram, id=id) if id else None
    if request.method == 'POST':
        form = PostInstagramForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('listar_instagram')
    else:
        form = PostInstagramForm(instance=post)
    titulo = "Editar Post da Vitrine" if id else "Novo Post da Vitrine"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_post_insta(request, id):
    post = get_object_or_404(PostInstagram, id=id)
    post.delete()
    return redirect('listar_instagram')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def editar_institucional(request):
    pagina, created = PaginaInstitucional.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = PaginaInstitucionalForm(request.POST, instance=pagina)
        if form.is_valid():
            form.save()
            return redirect('site_hub')
    else:
        form = PaginaInstitucionalForm(instance=pagina)
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': 'Editar Página Institucional'})