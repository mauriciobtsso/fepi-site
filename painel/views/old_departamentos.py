from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from blogs.models import BlogDepartamento
from painel.forms.blogs import BlogDepartamentoCreateForm

def listar_departamentos(request):
    # Lista todos os departamentos criados
    departamentos = BlogDepartamento.objects.all().order_by('nome')
    return render(request, 'painel/blogs/listar_departamentos.html', {'departamentos': departamentos})

def criar_departamento(request):
    if request.method == 'POST':
        form = BlogDepartamentoCreateForm(request.POST, request.FILES)
        if form.is_valid():
            departamento = form.save()
            messages.success(request, f'Blog para {departamento.nome} criado com sucesso!')
            return redirect('painel_listar_departamentos')
    else:
        form = BlogDepartamentoCreateForm()
        
    contexto = {
        'form': form,
        'titulo': 'Criar Novo Blog de Departamento',
        'acao': 'Criar Departamento'
    }
    return render(request, 'painel/blogs/form_departamento.html', contexto)