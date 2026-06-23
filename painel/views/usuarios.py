# painel/views/usuarios.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction

from usuarios.models import Perfil, PaginaSejaMembro
from painel.forms.usuarios import PaginaSejaMembroForm
from blogs.models import BlogDepartamento # <-- ADICIONADO AQUI
from .auth import is_admin

@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/painel/')
def gerenciar_usuarios(request):
    for su in User.objects.filter(is_superuser=True):
        Perfil.objects.get_or_create(
            user=su, 
            defaults={'nome_razao_social': 'Administrador do Sistema', 'tipo': 'PF', 'status': 'APROVADO'}
        )
    
    # Exclui o utilizador com o username exato 'admin' da lista
    perfis = Perfil.objects.exclude(user__username='admin').select_related('departamento_blog').order_by('-id')
    
    if request.method == 'POST':
        perfil_id = request.POST.get('perfil_id')
        acao = request.POST.get('acao')
        perfil = get_object_or_404(Perfil, id=perfil_id)
        
        if acao == 'aprovar':
            perfil.status = 'APROVADO'
            perfil.save()
            perfil.user.is_active = True
            perfil.user.save()
            messages.success(request, f"Cadastro de {perfil.user.username} APROVADO com sucesso.")
            
        elif acao == 'recusar':
            perfil.status = 'RECUSADO'
            perfil.save()
            perfil.user.is_active = False
            perfil.user.save()
            messages.error(request, f"Cadastro de {perfil.user.username} RECUSADO.")
            
        elif acao == 'toggle_colunista':
            perfil.is_colunista = not perfil.is_colunista
            perfil.save()
            status_col = "agora é Colunista" if perfil.is_colunista else "teve o acesso de Colunista removido"
            messages.info(request, f"{perfil.user.username} {status_col}.")
            
        return redirect('gerenciar_usuarios')
        
    return render(request, 'painel/usuarios/gerenciar_usuarios.html', {'perfis': perfis})

@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/painel/')
def criar_usuario(request):
    # Busca departamentos ativos para popular o select no template
    departamentos_disponiveis = BlogDepartamento.objects.filter(ativo=True).order_by('nome')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        nome = request.POST.get('nome_razao_social')
        tipo = request.POST.get('tipo')
        cpf_cnpj = request.POST.get('cpf_cnpj')
        data_nasc = request.POST.get('data_nascimento_fundacao') 
        telefone = request.POST.get('telefone')
        is_colunista = request.POST.get('is_colunista') == 'on'
        
        # Captura se a caixa de administrador foi marcada
        is_admin_system = request.POST.get('is_admin') == 'on'
        
        # Captura o vínculo do departamento
        departamento_blog_id = request.POST.get('departamento_blog_id')
        
        status = request.POST.get('status', 'APROVADO')
        is_active = True if status == 'APROVADO' else False

        try:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Este nome de utilizador já está em uso.")
                return render(request, 'painel/usuarios/form_usuario.html', {
                    'titulo': 'Novo Usuário',
                    'departamentos_disponiveis': departamentos_disponiveis
                })

            with transaction.atomic():
                user = User.objects.create_user(username=username, email=email, password=senha, is_active=is_active)
                
                # Aplica permissões de administrador se marcado
                if is_admin_system:
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                
                perfil = user.perfil
                perfil.nome_razao_social = nome
                perfil.tipo = tipo
                perfil.cpf_cnpj = cpf_cnpj
                perfil.data_nascimento_fundacao = data_nasc if data_nasc else None
                perfil.telefone = telefone
                perfil.cep = request.POST.get('cep')
                perfil.logradouro = request.POST.get('logradouro')
                perfil.numero = request.POST.get('numero')
                perfil.complemento = request.POST.get('complemento')
                perfil.bairro = request.POST.get('bairro')
                perfil.cidade = request.POST.get('cidade')
                perfil.estado = request.POST.get('estado')
                perfil.status = status
                perfil.is_colunista = is_colunista
                
                # Associa o departamento (se selecionado, pega o ID, senão fica nulo)
                perfil.departamento_blog_id = departamento_blog_id if departamento_blog_id else None
                
                perfil.save()

            messages.success(request, f"Utilizador {username} criado com sucesso!")
            return redirect('gerenciar_usuarios')
        except Exception as e:
            messages.error(request, f"Erro ao criar utilizador: {str(e)}")
            
    return render(request, 'painel/usuarios/form_usuario.html', {
        'titulo': 'Novo Usuário',
        'departamentos_disponiveis': departamentos_disponiveis
    })

@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/painel/')
def editar_usuario(request, id):
    perfil = get_object_or_404(Perfil, id=id)
    departamentos_disponiveis = BlogDepartamento.objects.filter(ativo=True).order_by('nome')
    
    # Proteção adicional: ninguém pode editar o 'admin' principal pelo painel
    if perfil.user.username == 'admin':
        messages.error(request, "Acesso Negado: O utilizador principal do sistema não pode ser alterado por aqui.")
        return redirect('gerenciar_usuarios')

    if request.method == 'POST':
        perfil.nome_razao_social = request.POST.get('nome_razao_social')
        perfil.tipo = request.POST.get('tipo')
        perfil.cpf_cnpj = request.POST.get('cpf_cnpj')
        
        data_nasc = request.POST.get('data_nascimento_fundacao')
        perfil.data_nascimento_fundacao = data_nasc if data_nasc else None 
        
        perfil.telefone = request.POST.get('telefone')
        perfil.is_colunista = request.POST.get('is_colunista') == 'on'
        
        perfil.cep = request.POST.get('cep')
        perfil.logradouro = request.POST.get('logradouro')
        perfil.numero = request.POST.get('numero')
        perfil.complemento = request.POST.get('complemento')
        perfil.bairro = request.POST.get('bairro')
        perfil.cidade = request.POST.get('cidade')
        perfil.estado = request.POST.get('estado')
        
        # 🔴 SALVA O DEPARTAMENTO
        departamento_blog_id = request.POST.get('departamento_blog_id')
        perfil.departamento_blog_id = departamento_blog_id if departamento_blog_id else None
        
        novo_status = request.POST.get('status')
        if novo_status:
            perfil.status = novo_status
            perfil.user.is_active = (novo_status == 'APROVADO')
            
        # Atualiza os privilégios de Administrador
        is_admin_system = request.POST.get('is_admin') == 'on'
        
        # Garante que um utilizador não retira o seu próprio acesso de admin sem querer
        if perfil.user == request.user and not is_admin_system:
            messages.warning(request, "Você não pode remover o seu próprio acesso de administrador.")
        else:
            perfil.user.is_staff = is_admin_system
            perfil.user.is_superuser = is_admin_system
        
        nova_senha = request.POST.get('nova_senha')
        if nova_senha:
            perfil.user.set_password(nova_senha)
            messages.info(request, "A palavra-passe do utilizador foi redefinida.")

        email = request.POST.get('email')
        if email:
            perfil.user.email = email
            
        perfil.user.save()
        perfil.save()
        
        messages.success(request, f"Dados de {perfil.user.username} atualizados com sucesso!")
        return redirect('gerenciar_usuarios')
        
    return render(request, 'painel/usuarios/form_usuario.html', {
        'perfil': perfil, 
        'titulo': f'Editar Usuário: {perfil.user.username}',
        'departamentos_disponiveis': departamentos_disponiveis
    })

@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/painel/')
def excluir_usuario(request, id):
    perfil = get_object_or_404(Perfil, id=id)
    if perfil.user == request.user:
        messages.error(request, "Segurança: Não pode excluir a sua própria conta por aqui.")
        return redirect('gerenciar_usuarios')
    
    if perfil.user.username == 'admin':
        messages.error(request, "Segurança: O administrador principal não pode ser excluído.")
        return redirect('gerenciar_usuarios')
        
    usuario = perfil.user
    usuario.delete()
    messages.success(request, "Utilizador excluído permanentemente.")
    return redirect('gerenciar_usuarios')

@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/painel/')
def editar_pagina_membro(request):
    pagina, created = PaginaSejaMembro.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        form = PaginaSejaMembroForm(request.POST, instance=pagina)
        if form.is_valid():
            form.save()
            messages.success(request, "Página Seja Membro atualizada com sucesso!")
            return redirect('site_hub') 
    else:
        form = PaginaSejaMembroForm(instance=pagina)
        
    return render(request, 'painel/programacao/form_generico.html', {
        'form': form, 
        'titulo': 'Editar Página "Seja Membro"', 
        'voltar_url': 'site_hub'
    })