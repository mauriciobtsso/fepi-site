# painel/views/intranet.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator
from intranet.models import DocumentoRestrito, CategoriaDocumento
from painel.forms import DocumentoForm, CategoriaDocForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_documentos(request):
    # Captura os parâmetros de busca
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    
    # Busca base: todos os documentos (ordenados pelo ID decrescente - mais recentes primeiro)
    documentos_list = DocumentoRestrito.objects.all().order_by('-id')
    
    # Filtro por texto
    if query:
        documentos_list = documentos_list.filter(titulo__icontains=query)
        
    # Filtro por categoria
    if categoria_id:
        documentos_list = documentos_list.filter(categoria_id=categoria_id)
        
    # Paginação (15 por página)
    paginator = Paginator(documentos_list, 15)
    page_number = request.GET.get('page')
    documentos = paginator.get_page(page_number)
    
    # Categorias para o menu dropdown do filtro
    categorias = CategoriaDocumento.objects.all().order_by('nome')
    
    return render(request, 'painel/listar_documentos.html', {
        'documentos': documentos,
        'query': query,
        'categoria_id': categoria_id,
        'categorias': categorias
    })

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def criar_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_documentos')
    else:
        form = DocumentoForm()
    return render(request, 'painel/form_documento.html', {'form': form, 'titulo': 'Novo Documento'})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def editar_documento(request, id):
    doc = get_object_or_404(DocumentoRestrito, id=id)
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            return redirect('listar_documentos')
    else:
        form = DocumentoForm(instance=doc)
    return render(request, 'painel/form_documento.html', {'form': form, 'titulo': 'Editar Documento'})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_documento(request, id):
    doc = get_object_or_404(DocumentoRestrito, id=id)
    if request.method == 'POST':
        doc.delete()
        return redirect('listar_documentos')
    return render(request, 'painel/confirmar_exclusao.html', {'objeto': doc.titulo, 'voltar_url': 'listar_documentos'})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_categorias_doc(request):
    categorias = CategoriaDocumento.objects.all()
    if request.method == 'POST':
        form = CategoriaDocForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_categorias_doc')
    else:
        form = CategoriaDocForm()
    return render(request, 'painel/listar_categorias_doc.html', {'categorias': categorias, 'form': form})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_categoria_doc(request, id):
    cat = get_object_or_404(CategoriaDocumento, id=id)
    try:
        cat.delete()
    except:
        pass 
    return redirect('listar_categorias_doc')