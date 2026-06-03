from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import DocumentoRestrito, CategoriaDocumento
from core.models import Coluna
from voluntarios.models import DocumentoVoluntario
from .forms import ColunaIntranetForm, IntranetVoluntarioForm

@login_required(login_url='/login/')
def area_federado(request):
    todas_categorias = CategoriaDocumento.objects.all()
    base_docs = DocumentoRestrito.objects.select_related('categoria').order_by('-data_publicacao')

    busca_atual = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria')

    try:
        categoria_id = int(categoria_id) if categoria_id else None
    except ValueError:
        categoria_id = None

    if busca_atual or categoria_id:
        modo_exibicao = 'lista'
        grupos = None
        if categoria_id:
            base_docs = base_docs.filter(categoria__id=categoria_id)
        if busca_atual:
            base_docs = base_docs.filter(Q(titulo__icontains=busca_atual) | Q(descricao__icontains=busca_atual))
        documentos_finais = base_docs
    else:
        modo_exibicao = 'agrupado'
        documentos_finais = None
        grupos = []
        for cat in todas_categorias:
            docs_da_categoria = base_docs.filter(categoria=cat)
            if docs_da_categoria.exists():
                grupos.append({'titulo_categoria': cat.nome, 'lista': docs_da_categoria})

    return render(request, 'intranet/dashboard.html', {
        'user': request.user,
        'modo_exibicao': modo_exibicao,
        'categorias': todas_categorias,
        'documentos': documentos_finais,
        'grupos': grupos,
        'busca_atual': busca_atual,
        'categoria_atual': categoria_id,
    })

# ==========================================
# ÁREA DO COLUNISTA
# ==========================================

@login_required(login_url='/login/')
def meus_artigos(request):
    # Trava de Segurança: Só entra se for colunista
    if not hasattr(request.user, 'perfil') or not request.user.perfil.is_colunista:
        messages.error(request, "Você não tem permissão para acessar o estúdio de redação.")
        return redirect('area_federado')

    # Busca apenas os artigos DESTE usuário logado
    artigos = Coluna.objects.filter(autor_usuario=request.user).order_by('-data_publicacao')
    return render(request, 'intranet/meus_artigos.html', {'artigos': artigos})

@login_required(login_url='/login/')
def redigir_artigo(request, pk=None):
    if not hasattr(request.user, 'perfil') or not request.user.perfil.is_colunista:
        return redirect('area_federado')

    if pk:
        artigo = get_object_or_404(Coluna, pk=pk, autor_usuario=request.user)
        # Trava: Não pode editar se já estiver aprovado e publicado (só admin pode)
        if artigo.status == 'PUBLICADO':
            messages.warning(request, "Este artigo já foi publicado e não pode ser alterado por aqui.")
            return redirect('meus_artigos')
    else:
        artigo = None

    if request.method == 'POST':
        form = ColunaIntranetForm(request.POST, request.FILES, instance=artigo)
        if form.is_valid():
            novo_artigo = form.save(commit=False)
            novo_artigo.autor_usuario = request.user
            
            # Verifica qual botão do HTML foi clicado
            if 'salvar_rascunho' in request.POST:
                novo_artigo.status = 'RASCUNHO'
                messages.success(request, 'Rascunho salvo com sucesso! Você pode continuar editando mais tarde.')
            elif 'enviar_revisao' in request.POST:
                novo_artigo.status = 'PENDENTE'
                messages.success(request, 'Artigo enviado para a diretoria! Assim que aprovado, será publicado no portal.')
                
            novo_artigo.save()
            return redirect('meus_artigos')
    else:
        form = ColunaIntranetForm(instance=artigo)

    return render(request, 'intranet/redigir_artigo.html', {'form': form, 'artigo': artigo})

# ==========================================
# PORTAL DO VOLUNTÁRIO
# ==========================================

@login_required(login_url='/login/')
def voluntariado_intro(request):
    """ Passo 1: Landing Page com regras e links """
    # Passamos para a tela se o usuário já é voluntário, para ocultar o botão de cadastro se necessário
    ja_e_voluntario = request.user.perfil.is_voluntario if hasattr(request.user, 'perfil') else False
    return render(request, 'intranet/voluntariado_intro.html', {'ja_e_voluntario': ja_e_voluntario})

@login_required(login_url='/login/')
def voluntariado_cadastro(request):
    """ Passo 2: Formulário de autoatendimento """
    if not hasattr(request.user, 'perfil'):
        messages.error(request, 'Erro: Perfil não encontrado.')
        return redirect('area_federado')

    perfil = request.user.perfil

    if request.method == 'POST':
        form = IntranetVoluntarioForm(request.POST, instance=perfil)
        
        if form.is_valid():
            voluntario_atualizado = form.save(commit=False)
            voluntario_atualizado.is_voluntario = True  # Mágica: Ativa a flag de voluntário no Cadastro Único
            
            # Se for o primeiro cadastro, marca a data de início como hoje
            if not voluntario_atualizado.data_inicio_voluntariado:
                voluntario_atualizado.data_inicio_voluntariado = timezone.now().date()
                
            voluntario_atualizado.save()

            # Captura os arquivos enviados manualmente pelo formulário HTML (sem usar o form.py)
            if 'arquivo_termo' in request.FILES:
                DocumentoVoluntario.objects.update_or_create(
                    voluntario=perfil,
                    tipo='Termo',
                    arquivo=request.FILES['arquivo_termo'],
                    data_referencia=timezone.now().date()
                )

            if 'arquivo_certidao' in request.FILES:
                DocumentoVoluntario.objects.update_or_create(
                    voluntario=perfil,
                    tipo='Certidao',
                    arquivo=request.FILES['arquivo_certidao'],
                    data_referencia=timezone.now().date()
                )

            messages.success(request, 'Dados salvos! Agora, por favor, imprima seu termo ou anexe os documentos pendentes.')
            return redirect('voluntariado_intro')
    else:
        form = IntranetVoluntarioForm(instance=perfil)

    return render(request, 'intranet/voluntariado_cadastro.html', {'form': form, 'perfil': perfil})