# painel/views/noticias.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.text import slugify
from django.utils import timezone
from noticias.models import Noticia
from painel.forms import NoticiaForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def criar_noticia(request):
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)
            if not noticia.slug:
                noticia.slug = slugify(noticia.titulo)
            noticia.save()
            return redirect('painel_home')
    else:
        form = NoticiaForm(initial={'data_publicacao': timezone.now(), 'autor': 'FEPI'})
    return render(request, 'painel/criar_noticia.html', {'form': form})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_noticias(request):
    noticias = Noticia.objects.all().order_by('-data_publicacao')
    return render(request, 'painel/listar_noticias.html', {'noticias': noticias})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def editar_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id=noticia_id)
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            form.save()
            return redirect('listar_noticias')
    else:
        form = NoticiaForm(instance=noticia)
    return render(request, 'painel/criar_noticia.html', {'form': form})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def deletar_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id=noticia_id)
    noticia.delete()
    return redirect('listar_noticias')