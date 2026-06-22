# painel/views/blogs.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.db.models import Q

from blogs.models import PostBlog, BlogDepartamento, CategoriaBlog
from painel.forms.blogs import PostBlogForm, ConfigBlogForm, BlogDepartamentoCreateForm, CategoriaBlogForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def blogs_hub(request):
    # 1. Captura o termo de busca (se existir)
    query = request.GET.get('q', '')

    # 2. Busca e Filtra os Departamentos
    departamentos = BlogDepartamento.objects.filter(ativo=True).order_by('nome')
    if query:
        departamentos = departamentos.filter(
            Q(nome__icontains=query) | 
            Q(subdominio__icontains=query)
        )

    # 3. Busca e Filtra os Artigos
    posts_list = PostBlog.objects.select_related('departamento', 'categoria').all().order_by('-data_publicacao')
    if query:
        posts_list = posts_list.filter(
            Q(titulo__icontains=query) | 
            Q(departamento__nome__icontains=query) |
            Q(departamento__subdominio__icontains=query)
        )

    # 4. Paginação dos Artigos (10 artigos por página)
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts_paginados = paginator.get_page(page_number)

    contexto = {
        'departamentos': departamentos,
        'posts': posts_paginados,
        'query': query, # Mantém a string de pesquisa no form
    }
    return render(request, 'painel/blogs/blogs_hub.html', contexto)


@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def criar_departamento(request):
    """ View para criar novos ambientes de blog diretamente pelo painel """
    if request.method == 'POST':
        form = BlogDepartamentoCreateForm(request.POST, request.FILES)
        if form.is_valid():
            departamento = form.save()
            messages.success(request, f'Ambiente para {departamento.nome} criado com sucesso!')
            return redirect('blogs_hub')
    else:
        form = BlogDepartamentoCreateForm()
        
    contexto = {
        'form': form,
        'titulo': 'Criar Novo Blog de Departamento',
        'acao': 'Criar Departamento'
    }
    return render(request, 'painel/blogs/form_departamento.html', contexto)


@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_post_blog(request, id=None):
    instancia = get_object_or_404(PostBlog, id=id) if id else None
    if request.method == 'POST':
        form = PostBlogForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            post = form.save(commit=False)
            if not post.slug:
                post.slug = slugify(post.titulo)
            if not post.autor and request.user:
                post.autor = request.user
            post.save()
            messages.success(request, "Publicação do blog salva com sucesso!")
            return redirect('blogs_hub')
    else:
        form = PostBlogForm(instance=instancia)
        
    titulo = "Editar Postagem do Blog" if id else "Nova Publicação para o Blog"
    return render(request, 'painel/blogs/form_post.html', {'form': form, 'titulo': titulo})


@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_post_blog(request, id):
    post = get_object_or_404(PostBlog, id=id)
    post.delete()
    messages.success(request, "Postagem excluída permanentemente.")
    return redirect('blogs_hub')


@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def configurar_rede_social_blog(request, depto_id):
    depto = get_object_or_404(BlogDepartamento, id=depto_id)
    if request.method == 'POST':
        form = ConfigBlogForm(request.POST, request.FILES, instance=depto)
        if form.is_valid():
            form.save()
            messages.success(request, f"Configurações e Instagram de {depto.nome} atualizados!")
            return redirect('blogs_hub')
    else:
        form = ConfigBlogForm(instance=depto)
    
    return render(request, 'painel/programacao/form_generico.html', {
        'form': form, 
        'titulo': f'Configurar Blog & Instagram: {depto.nome}'
    })

# =========================================================
# GERENCIAMENTO DE CATEGORIAS (TAGS) DOS BLOGS
# =========================================================

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_categorias_blog(request):
    categorias = CategoriaBlog.objects.all()
    return render(request, 'painel/blogs/listar_categorias.html', {'categorias': categorias})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_categoria_blog(request, id=None):
    instancia = get_object_or_404(CategoriaBlog, id=id) if id else None
    if request.method == 'POST':
        form = CategoriaBlogForm(request.POST, instance=instancia)
        if form.is_valid():
            categoria = form.save(commit=False)
            if not categoria.slug:
                categoria.slug = slugify(categoria.nome)
            categoria.save()
            msg = "Categoria atualizada com sucesso!" if id else "Categoria criada com sucesso!"
            messages.success(request, msg)
            return redirect('listar_categorias_blog')
    else:
        form = CategoriaBlogForm(instance=instancia)
        
    titulo = "Editar Categoria do Blog" if id else "Nova Categoria para Blogs"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_categoria_blog(request, id):
    categoria = get_object_or_404(CategoriaBlog, id=id)
    categoria.delete()
    messages.success(request, "Categoria excluída com sucesso.")
    return redirect('listar_categorias_blog')