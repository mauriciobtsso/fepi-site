# painel/views/intranet.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from intranet.models import DocumentoRestrito, CategoriaDocumento
from painel.forms import DocumentoForm, CategoriaDocForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_documentos(request):
    documentos = DocumentoRestrito.objects.all()
    return render(request, 'painel/listar_documentos.html', {'documentos': documentos})

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