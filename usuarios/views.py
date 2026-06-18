from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

# Importamos a central de e-mails da FEPI
from core.utils import enviar_email_sistema
from .models import PaginaSejaMembro

def seja_membro(request):
    pagina_membro = PaginaSejaMembro.objects.first()

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        nome = request.POST.get('nome_razao_social')
        cpf_cnpj = request.POST.get('cpf_cnpj')
        data_nasc = request.POST.get('data_nascimento_fundacao')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        senha = request.POST.get('senha')
        
        cep = request.POST.get('cep')
        logradouro = request.POST.get('logradouro')
        numero = request.POST.get('numero')
        complemento = request.POST.get('complemento')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')

        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            messages.error(request, "Este e-mail já está cadastrado em nosso sistema.")
            return redirect('seja_membro')

        try:
            with transaction.atomic():
                user = User.objects.create_user(username=email, email=email, password=senha, is_active=False)
                
                perfil = user.perfil
                perfil.tipo = tipo
                perfil.nome_razao_social = nome
                perfil.cpf_cnpj = cpf_cnpj
                perfil.data_nascimento_fundacao = data_nasc if data_nasc else None
                perfil.telefone = telefone # <--- AQUI ESTAVA O ERRO (telephone)
                perfil.cep = cep
                perfil.logradouro = logradouro
                perfil.numero = numero
                perfil.complemento = complemento
                perfil.bairro = bairro
                perfil.cidade = cidade
                perfil.estado = estado
                perfil.status = 'PENDENTE'
                perfil.save()
                
            # Dispara o e-mail de Boas-Vindas usando o template HTML profissional
            enviar_email_sistema(
                assunto="Recebemos sua solicitação de cadastro! - FEPI",
                corpo="",
                destinatarios=[email],
                template_name="emails/boas_vindas.html",
                context={"nome": nome}
            )
                
            messages.success(request, "Cadastro realizado com sucesso! Sua solicitação foi enviada para a diretoria. Você só conseguirá acessar o sistema após a aprovação.")
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao processar seu cadastro: {str(e)}")
            return redirect('seja_membro')

    context = {
        'pagina_membro': pagina_membro,
    }
    return render(request, 'usuarios/seja_membro.html', context)

@login_required(login_url='/login/')
def minha_conta(request):
    user = request.user
    perfil = user.perfil

    if request.method == 'POST':
        if 'atualizar_dados' in request.POST:
            perfil.nome_razao_social = request.POST.get('nome_razao_social')
            data_nasc = request.POST.get('data_nascimento_fundacao')
            perfil.data_nascimento_fundacao = data_nasc if data_nasc else None
            perfil.telefone = request.POST.get('telefone')
            perfil.cep = request.POST.get('cep')
            perfil.logradouro = request.POST.get('logradouro')
            perfil.numero = request.POST.get('numero')
            perfil.complemento = request.POST.get('complemento')
            perfil.bairro = request.POST.get('bairro')
            perfil.cidade = request.POST.get('cidade')
            perfil.estado = request.POST.get('estado')
            perfil.save()
            
            messages.success(request, "Seus dados foram atualizados com sucesso!")
            return redirect('minha_conta')

        elif 'alterar_senha' in request.POST:
            senha_atual = request.POST.get('senha_atual')
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')

            if not user.check_password(senha_atual):
                messages.error(request, "Sua senha atual está incorreta.")
            elif nova_senha != confirmar_senha:
                messages.error(request, "A nova senha e a confirmação não coincidem.")
            elif len(nova_senha) < 6:
                messages.error(request, "A nova senha deve ter pelo menos 6 caracteres.")
            else:
                user.set_password(nova_senha)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Sua senha foi alterada com sucesso!")
            
            return redirect('minha_conta')

    return render(request, 'usuarios/minha_conta.html', {'perfil': perfil})