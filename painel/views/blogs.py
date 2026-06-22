# painel/views/blogs.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.text import slugify
from blogs.models import PostBlog, BlogDepartamento
from painel.forms import PostBlogForm, ConfigBlogForm
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def blogs_hub(request):
    # Lista todos os departamentos para o Admin gerenciar, ou o voluntário vê as opções
    departamentos = BlogDepartamento.objects.filter(ativo=True)
    posts = PostBlog.objects.all().select_related('departamento').order_by('-data_publicacao')
    
    return render(request, 'painel/blogs/blogs_hub.html', {
        'departamentos': departamentos,
        'posts': posts
    })

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
    
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': f'Configurar Blog & Instagram: {depto.nome}'})