# painel/views/noticias.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
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
            return redirect('listar_noticias') # Corrigido para a lista
        else:
            # 🔴 ADICIONE ESTA LINHA PARA DEBUGAR
            print(form.errors) 
    else:
        form = NoticiaForm(initial={'data_publicacao': timezone.now(), 'autor': 'FEPI'})
    return render(request, 'painel/criar_noticia.html', {'form': form})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_noticias(request):
    # Pega o termo digitado na barra de busca (se houver)
    query = request.GET.get('q', '')
    
    # Busca base: todas as notícias ordenadas
    noticias_list = Noticia.objects.all().order_by('-data_publicacao')
    
    # Se o usuário digitou algo, filtra por título, resumo ou autor
    if query:
        noticias_list = noticias_list.filter(
            Q(titulo__icontains=query) |
            Q(resumo__icontains=query) |
            Q(autor__icontains=query)
        )
        
    # Paginação: 10 notícias por página
    paginator = Paginator(noticias_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'painel/listar_noticias.html', {
        'page_obj': page_obj,
        'query': query  # Passamos a query para manter a busca ativa nas páginas
    })

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