from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from noticias.models import Noticia
from painel.forms import NoticiaForm
from .auth import check_acesso_painel
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

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
            return redirect('listar_noticias')
        else:
            print(form.errors) 
    else:
        form = NoticiaForm(initial={'data_publicacao': timezone.now(), 'autor': 'FEPI'})
    return render(request, 'painel/criar_noticia.html', {'form': form})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_noticias(request):
    query = request.GET.get('q', '')
    noticias_list = Noticia.objects.all().order_by('-data_publicacao')
    
    if query:
        noticias_list = noticias_list.filter(
            Q(titulo__icontains=query) |
            Q(resumo__icontains=query) |
            Q(autor__icontains=query)
        )
        
    paginator = Paginator(noticias_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'painel/listar_noticias.html', {
        'page_obj': page_obj,
        'query': query
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
    noticia = get_object_or_404(Noticia, id=noticia_mid)
    noticia.delete()
    return redirect('listar_noticias')

@csrf_exempt
@login_required(login_url='/login/')
def upload_imagem_editorjs_custom(request):
    """
    Rota customizada para receber imagens e GIFs do EditorJS, com verificação de tamanho
    para respeitar o limite de 10MB do plano gratuito do Cloudinary.
    """
    if request.method == 'POST' and request.FILES.get('image'):
        arquivo = request.FILES['image']
        
        # Limite de 10MB (10485760 bytes)
        MAX_SIZE = 10 * 1024 * 1024 
        
        if arquivo.size > MAX_SIZE:
            return JsonResponse({
                "success": 0,
                "error": "Arquivo muito grande. O limite máximo é 10MB."
            })
        
        try:
            # Salva no Cloudinary via default_storage
            nome_salvo = default_storage.save(f"noticias_editorjs/{arquivo.name}", arquivo)
            url_final = default_storage.url(nome_salvo)
            
            return JsonResponse({
                "success": 1,
                "file": {
                    "url": url_final
                }
            })
        except Exception as e:
            print(f"Erro ao fazer upload no Editor.js: {e}")
            return JsonResponse({
                "success": 0, 
                "error": "Erro ao processar o upload no servidor."
            })
            
    return JsonResponse({"success": 0})