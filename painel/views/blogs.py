# painel/views/blogs.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.db.models import Q

from blogs.models import PostBlog, BlogDepartamento, CategoriaBlog, BlogMembro
from painel.forms.blogs import PostBlogForm, ConfigBlogForm, BlogDepartamentoCreateForm, CategoriaBlogForm
from .auth import check_acesso_painel, is_admin


def blogs_permitidos(user):
    """Blogs que o usuário pode administrar; superusuário mantém acesso global."""
    if user.is_superuser:
        return BlogDepartamento.objects.all()
    legado = getattr(getattr(user, 'perfil', None), 'departamento_blog_id', None)
    qs = BlogDepartamento.objects.filter(membros__usuario=user, membros__ativo=True)
    if legado:
        qs = qs | BlogDepartamento.objects.filter(pk=legado)
    return qs.distinct()


def membro_do_blog(user, blog):
    if user.is_superuser:
        return None
    return BlogMembro.objects.filter(usuario=user, blog=blog, ativo=True).first()


def pode_acessar_blog(user, blog):
    return user.is_superuser or membro_do_blog(user, blog) is not None


def pode_configurar_blog(user, blog):
    membro = membro_do_blog(user, blog)
    return user.is_superuser or (membro and membro.papel == BlogMembro.PAPEL_GESTOR)


def pode_excluir_blog(user, blog):
    return user.is_superuser


def aplicar_escopo_formulario(form, user):
    if not user.is_superuser:
        form.fields['departamento'].queryset = blogs_permitidos(user).filter(ativo=True)
        membro_blogs = BlogMembro.objects.filter(usuario=user, ativo=True).values_list('blog_id', flat=True)
        if not form.instance.pk:
            form.fields['publicado'].initial = False
        if not form.instance.pk or form.instance.departamento_id in membro_blogs:
            form.fields['publicado'].disabled = True
    return form

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def blogs_hub(request):
    # 1. Captura o termo de busca (se existir)
    query = request.GET.get('q', '')

    # 2. Busca e Filtra os Departamentos
    departamentos = blogs_permitidos(request.user).filter(ativo=True).order_by('nome')
    if query:
        departamentos = departamentos.filter(
            Q(nome__icontains=query) | 
            Q(subdominio__icontains=query)
        )

    # 3. Busca e Filtra os Artigos
    posts_list = PostBlog.objects.select_related('departamento', 'categoria').filter(departamento__in=blogs_permitidos(request.user)).order_by('-data_publicacao')
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
@user_passes_test(is_admin, login_url='/usuarios/minha-conta/')
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
    if instancia and not pode_acessar_blog(request.user, instancia.departamento):
        return redirect('blogs_hub')
    if request.method == 'POST':
        form = aplicar_escopo_formulario(PostBlogForm(request.POST, request.FILES, instance=instancia), request.user)
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
        form = aplicar_escopo_formulario(PostBlogForm(instance=instancia), request.user)
        
    titulo = "Editar Postagem do Blog" if id else "Nova Publicação para o Blog"
    return render(request, 'painel/blogs/form_post.html', {'form': form, 'titulo': titulo})


@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_post_blog(request, id):
    post = get_object_or_404(PostBlog, id=id, departamento__in=blogs_permitidos(request.user))
    post.delete()
    messages.success(request, "Postagem excluída permanentemente.")
    return redirect('blogs_hub')


@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def configurar_rede_social_blog(request, depto_id):
    depto = get_object_or_404(BlogDepartamento, id=depto_id)
    if not pode_configurar_blog(request.user, depto):
        return redirect('blogs_hub')
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
    return redirect('listar_categorias_blog')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_departamento_blog(request, id):
    """
    View para excluir um departamento de blog.
    Ao excluir um departamento, todos os seus posts também serão removidos
    (cascata de exclusão definida no modelo).
    """
    departamento = get_object_or_404(BlogDepartamento, id=id)
    if not pode_excluir_blog(request.user, departamento):
        return redirect('blogs_hub')
    nome_departamento = departamento.nome
    
    # Excluir o departamento (e todos os posts associados em cascata)
    departamento.delete()
    
    messages.success(
        request, 
        f"Departamento '{nome_departamento}' e todos os seus posts foram excluídos permanentemente."
    )
    return redirect('blogs_hub')
