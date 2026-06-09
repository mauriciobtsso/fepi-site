# painel/views/livraria.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from livraria.models import Livro, Categoria as CategoriaLivro, LivrariaConfig
from painel.forms import LivroForm, CategoriaLivroForm, LivrariaConfigForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def livraria_hub(request):
    return render(request, 'painel/livraria/livraria_hub.html')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_livros(request):
    livros = Livro.objects.select_related('categoria').all().order_by('titulo')
    return render(request, 'painel/livraria/listar_livros.html', {'livros': livros})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_livro(request, id=None):
    instancia = get_object_or_404(Livro, id=id) if id else None
    if request.method == 'POST':
        form = LivroForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('listar_livros')
    else:
        form = LivroForm(instance=instancia)
    titulo = "Editar Livro" if id else "Novo Livro"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_livro(request, id):
    livro = get_object_or_404(Livro, id=id)
    livro.delete()
    return redirect('listar_livros')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_categorias_liv(request):
    categorias = CategoriaLivro.objects.all()
    if request.method == 'POST':
        form = CategoriaLivroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_categorias_liv')
    else:
        form = CategoriaLivroForm()
    return render(request, 'painel/livraria/listar_categorias.html', {'categorias': categorias, 'form': form})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_categoria_liv(request, id):
    cat = get_object_or_404(CategoriaLivro, id=id)
    if not cat.livro_set.exists():
        cat.delete()
    return redirect('listar_categorias_liv')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def config_livraria(request):
    config, created = LivrariaConfig.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = LivrariaConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            return redirect('livraria_hub')
    else:
        form = LivrariaConfigForm(instance=config)
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': 'Configuração da Livraria'})