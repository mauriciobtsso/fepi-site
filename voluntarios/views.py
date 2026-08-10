#voluntarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import engines
import html
from django.db.models import Q
from django.core.paginator import Paginator

from .models import DocumentoVoluntario, ModeloTermoVoluntario
from .forms import VoluntarioForm, DocumentoVoluntarioForm, ModeloTermoForm
from usuarios.models import Perfil

@login_required
def listar_voluntarios(request):
    query = request.GET.get('q', '')
    voluntarios_list = Perfil.objects.filter(is_voluntario=True).order_by('-id')
    
    if query:
        voluntarios_list = voluntarios_list.filter(
            Q(nome_razao_social__icontains=query) |
            Q(cpf_cnpj__icontains=query) |
            Q(telefone__icontains=query)
        )
    
    paginator = Paginator(voluntarios_list, 15)
    page_number = request.GET.get('page')
    voluntarios = paginator.get_page(page_number)
    
    return render(request, 'voluntarios/listar_voluntarios.html', {
        'voluntarios': voluntarios,
        'query': query,
    })

@login_required
def cadastrar_voluntario(request):
    if request.method == 'POST':
        form = VoluntarioForm(request.POST, request.FILES)
        if form.is_valid():
            voluntario = form.save(commit=False)
            voluntario.is_voluntario = True 
            voluntario.save()
            messages.success(request, 'Voluntário cadastrado com sucesso!')
            return redirect('listar_voluntarios')
    else:
        form = VoluntarioForm()
    return render(request, 'voluntarios/form_voluntario.html', {'form': form, 'titulo': 'Cadastrar Voluntário'})

@login_required
def documentos_voluntario(request, pk):
    voluntario = get_object_or_404(Perfil, pk=pk, is_voluntario=True)
    documentos = voluntario.documentos_voluntario.all()
    
    if request.method == 'POST':
        form = DocumentoVoluntarioForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.voluntario = voluntario 
            doc.save()
            messages.success(request, 'Documento anexado com sucesso!')
            return redirect('documentos_voluntario', pk=voluntario.pk)
    else:
        form = DocumentoVoluntarioForm()
        
    return render(request, 'voluntarios/documentos_voluntario.html', {
        'voluntario': voluntario,
        'documentos': documentos,
        'form': form
    })

@login_required
def excluir_documento_voluntario(request, pk):
    doc = get_object_or_404(DocumentoVoluntario, pk=pk)
    voluntario_pk = doc.voluntario.pk
    doc.delete()
    messages.success(request, 'Documento removido do histórico.')
    return redirect('documentos_voluntario', pk=voluntario_pk)

@login_required
def editar_voluntario(request, pk):
    voluntario = get_object_or_404(Perfil, pk=pk, is_voluntario=True)
    if request.method == 'POST':
        form = VoluntarioForm(request.POST, request.FILES, instance=voluntario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('listar_voluntarios')
    else:
        form = VoluntarioForm(instance=voluntario)
    return render(request, 'voluntarios/form_voluntario.html', {'form': form, 'titulo': 'Editar Voluntário', 'voluntario': voluntario})

@login_required
def excluir_voluntario(request, pk):
    voluntario = get_object_or_404(Perfil, pk=pk, is_voluntario=True)
    if request.method == 'POST':
        voluntario.is_voluntario = False
        voluntario.save()
        messages.success(request, 'Cadastro de voluntário desativado.')
        return redirect('listar_voluntarios')
    return render(request, 'voluntarios/confirmar_exclusao.html', {'voluntario': voluntario})

@login_required
def editar_modelo_termo(request):
    modelo, created = ModeloTermoVoluntario.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        form = ModeloTermoForm(request.POST, instance=modelo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Modelo do Termo atualizado com sucesso!')
            return redirect('listar_voluntarios')
    else:
        form = ModeloTermoForm(instance=modelo)
        
    return render(request, 'voluntarios/editar_modelo_termo.html', {'form': form})

@login_required
def imprimir_termo(request, pk):
    voluntario = get_object_or_404(Perfil, pk=pk, is_voluntario=True)
    
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

    # 2. Configurações dos campos _display
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

    # 3. Tags de Data Automática (Emissão)
    from django.utils import timezone
    hoje = timezone.now()
    meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    context_dict['dia'] = hoje.strftime("%d")
    context_dict['mes_nome'] = meses[hoje.month]
    context_dict['ano'] = hoje.strftime("%Y")

    modelo = ModeloTermoVoluntario.objects.filter(id=1).first()
    
    if modelo and modelo.conteudo:
        conteudo_limpo = html.unescape(modelo.conteudo)
        try:
            django_engine = engines['django']
            template_dinamico = django_engine.from_string(conteudo_limpo)
            conteudo_renderizado = template_dinamico.render(context_dict)
        except Exception as e:
            conteudo_renderizado = f"<div class='alert alert-danger text-center'><strong>Erro no formato das variáveis no CKEditor:</strong> {e}</div>{conteudo_limpo}"
    else:
        conteudo_renderizado = "<div class='alert alert-warning text-center'>O modelo do termo ainda não foi configurado. Vá no painel e clique em 'Configurar Termo'.</div>"

    return render(request, 'voluntarios/imprimir_termo.html', {
        'conteudo_renderizado': conteudo_renderizado,
        'voluntario': voluntario
    })