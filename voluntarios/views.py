from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import engines
from .models import Voluntario, DocumentoVoluntario, ModeloTermoVoluntario
from .forms import VoluntarioForm, DocumentoVoluntarioForm, ModeloTermoForm
import html
from django.db.models import Q
from django.core.paginator import Paginator

@login_required
def listar_voluntarios(request):
    # Pega o termo de busca na URL (se existir)
    query = request.GET.get('q', '')
    
    voluntarios_list = Voluntario.objects.all().order_by('-data_cadastro')
    
    # Se o usuário digitou algo, filtra por Nome OU CPF OU Telefone
    if query:
        voluntarios_list = voluntarios_list.filter(
            Q(nome__icontains=query) |
            Q(cpf__icontains=query) |
            Q(telefones__icontains=query)
        )
    
    # Paginação: 15 voluntários por página
    paginator = Paginator(voluntarios_list, 15)
    page_number = request.GET.get('page')
    voluntarios = paginator.get_page(page_number)
    
    return render(request, 'voluntarios/listar_voluntarios.html', {
        'voluntarios': voluntarios,
        'query': query, # Passamos a query de volta para manter na barra de pesquisa
    })

@login_required
def cadastrar_voluntario(request):
    if request.method == 'POST':
        form = VoluntarioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Voluntário cadastrado com sucesso!')
            return redirect('listar_voluntarios')
    else:
        form = VoluntarioForm()
    return render(request, 'voluntarios/form_voluntario.html', {'form': form, 'titulo': 'Cadastrar Voluntário'})

@login_required
def documentos_voluntario(request, pk):
    """Página dedicada ao histórico de arquivos de um voluntário específico"""
    voluntario = get_object_or_404(Voluntario, pk=pk)
    documentos = voluntario.documentos.all()
    
    if request.method == 'POST':
        form = DocumentoVoluntarioForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.voluntario = voluntario # Vincula o arquivo a este voluntário
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
    voluntario = get_object_or_404(Voluntario, pk=pk)
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
    voluntario = get_object_or_404(Voluntario, pk=pk)
    if request.method == 'POST':
        voluntario.delete()
        messages.success(request, 'Voluntário removido.')
        return redirect('listar_voluntarios')
    return render(request, 'voluntarios/confirmar_exclusao.html', {'voluntario': voluntario})

@login_required
def editar_modelo_termo(request):
    # Pega o modelo existente ou cria um novo se não existir (ID 1)
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
    voluntario = get_object_or_404(Voluntario, pk=pk)
    
    # 1. Prepara as variáveis
    campos = ['cpf', 'rg', 'cep', 'nome_pai', 'nome_mae', 'telefones', 'atividade_profissional', 'tipo_servico', 'dias_horarios', 'email']
    context_dict = {'voluntario': voluntario}
    
    for campo in campos:
        valor = getattr(voluntario, campo)
        context_dict[f'{campo}_display'] = valor if valor else "___________________________"
    
    # Endereço formatado
    rua = voluntario.endereco if voluntario.endereco else "________________"
    num = f", nº {voluntario.numero}" if voluntario.numero else ""
    bairro = f", {voluntario.bairro}" if voluntario.bairro else ""
    comp = f" ({voluntario.complemento})" if voluntario.complemento else ""
    context_dict['endereco_display'] = f"{rua}{num}{bairro}{comp}"

    # Vigência
    inicio = voluntario.data_inicio.strftime("%d/%m/%Y") if voluntario.data_inicio else "____/____/____"
    termino = voluntario.data_termino.strftime("%d/%m/%Y") if voluntario.data_termino else "____/____/____"
    context_dict['prazo_display'] = f"de {inicio} a {termino}"

    # 2. Busca o Modelo Exato (ID=1)
    modelo = ModeloTermoVoluntario.objects.filter(id=1).first()
    
    if modelo and modelo.conteudo:
        # A MÁGICA DE LIMPEZA: Reverte o &#123; de volta para { caso o CKEditor tenha bagunçado
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