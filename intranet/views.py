from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import engines
import html

from .models import DocumentoRestrito, CategoriaDocumento
from core.models import Coluna
from voluntarios.models import DocumentoVoluntario, ModeloTermoVoluntario
from voluntarios.forms import VoluntarioForm, DocumentoVoluntarioForm
from .forms import ColunaIntranetForm

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
    if not hasattr(request.user, 'perfil') or not request.user.perfil.is_colunista:
        messages.error(request, "Você não tem permissão para acessar o estúdio de redação.")
        return redirect('area_federado')

    artigos = Coluna.objects.filter(autor_usuario=request.user).order_by('-data_publicacao')
    return render(request, 'intranet/meus_artigos.html', {'artigos': artigos})

@login_required(login_url='/login/')
def redigir_artigo(request, pk=None):
    if not hasattr(request.user, 'perfil') or not request.user.perfil.is_colunista:
        return redirect('area_federado')

    if pk:
        artigo = get_object_or_404(Coluna, pk=pk, autor_usuario=request.user)
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
# PORTAL DO VOLUNTÁRIO (AUTOATENDIMENTO)
# ==========================================

@login_required(login_url='/login/')
def voluntariado_intro(request):
    ja_e_voluntario = request.user.perfil.is_voluntario if hasattr(request.user, 'perfil') else False
    return render(request, 'intranet/voluntariado_intro.html', {'ja_e_voluntario': ja_e_voluntario})

@login_required(login_url='/login/')
def voluntariado_cadastro(request):
    if not hasattr(request.user, 'perfil'):
        messages.error(request, 'Erro: Perfil não encontrado.')
        return redirect('area_federado')

    perfil = request.user.perfil

    # MUDANÇA: Removida a trava. Agora ele pode acessar essa tela para RENOVAR o termo e dados!

    if request.method == 'POST':
        form = VoluntarioForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            voluntario = form.save(commit=False)
            voluntario.is_voluntario = True
            voluntario.save()
            
            messages.success(request, 'Dados salvos com sucesso! Se você alterou o período de vigência, gere o seu novo termo e faça o upload.')
            return redirect('voluntariado_painel')
    else:
        form = VoluntarioForm(instance=perfil)

    return render(request, 'intranet/voluntariado_cadastro.html', {'form': form, 'perfil': perfil})

@login_required(login_url='/login/')
def voluntariado_painel(request):
    perfil = request.user.perfil
    if not perfil.is_voluntario:
        return redirect('voluntariado_intro')

    documentos = perfil.documentos_voluntario.all()

    if request.method == 'POST':
        form_doc = DocumentoVoluntarioForm(request.POST, request.FILES)
        if form_doc.is_valid():
            doc = form_doc.save(commit=False)
            doc.voluntario = perfil
            doc.save()
            messages.success(request, 'Documento anexado com sucesso!')
            return redirect('voluntariado_painel')
    else:
        form_doc = DocumentoVoluntarioForm()

    return render(request, 'intranet/voluntariado_painel.html', {
        'perfil': perfil,
        'documentos': documentos,
        'form_doc': form_doc
    })

@login_required(login_url='/login/')
def voluntariado_imprimir_termo(request):
    voluntario = request.user.perfil
    if not voluntario.is_voluntario:
        return redirect('voluntariado_intro')
    
    # 1. POLYFILL: Injetamos as variáveis antigas no objeto para o CKEditor ler perfeitamente
    voluntario.nome = voluntario.nome_razao_social
    voluntario.data_nascimento = voluntario.data_nascimento_fundacao
    
    if voluntario.cidade and voluntario.estado:
        voluntario.cidade_estado = f"{voluntario.cidade}/{voluntario.estado}"
    elif voluntario.cidade:
        voluntario.cidade_estado = voluntario.cidade
    elif voluntario.estado:
        voluntario.cidade_estado = voluntario.estado
    else:
        voluntario.cidade_estado = ""

    campos = ['rg', 'cep', 'nome_pai', 'nome_mae', 'atividade_profissional', 'tipo_servico', 'dias_horarios', 'site']
    context_dict = {'voluntario': voluntario}
    
    context_dict['cpf_display'] = voluntario.cpf_cnpj if voluntario.cpf_cnpj else "___________________________"
    context_dict['telefones_display'] = voluntario.telefone if voluntario.telefone else "___________________________"
    context_dict['email_display'] = voluntario.user.email if (voluntario.user and voluntario.user.email) else "___________________________"

    for campo in campos:
        valor = getattr(voluntario, campo, None)
        context_dict[f'{campo}_display'] = valor if valor else "___________________________"
    
    rua = voluntario.logradouro if voluntario.logradouro else "________________"
    num = f", nº {voluntario.numero}" if voluntario.numero else ""
    bairro = f", {voluntario.bairro}" if voluntario.bairro else ""
    comp = f" ({voluntario.complemento})" if voluntario.complemento else ""
    context_dict['endereco_display'] = f"{rua}{num}{bairro}{comp}"

    inicio = voluntario.data_inicio_voluntariado.strftime("%d/%m/%Y") if voluntario.data_inicio_voluntariado else "____/____/____"
    termino = voluntario.data_termino_voluntariado.strftime("%d/%m/%Y") if voluntario.data_termino_voluntariado else "____/____/____"
    context_dict['prazo_display'] = f"de {inicio} a {termino}"

    modelo = ModeloTermoVoluntario.objects.filter(id=1).first()
    
    if modelo and modelo.conteudo:
        conteudo_limpo = html.unescape(modelo.conteudo)
        try:
            django_engine = engines['django']
            template_dinamico = django_engine.from_string(conteudo_limpo)
            conteudo_renderizado = template_dinamico.render(context_dict)
        except Exception as e:
            conteudo_renderizado = f"<div class='alert alert-danger text-center'><strong>Erro no formato das variáveis:</strong> {e}</div>{conteudo_limpo}"
    else:
        conteudo_renderizado = "<div class='alert alert-warning text-center'>O modelo do termo ainda não foi configurado.</div>"

    return render(request, 'voluntarios/imprimir_termo.html', {
        'conteudo_renderizado': conteudo_renderizado,
        'voluntario': voluntario
    })