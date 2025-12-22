from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.utils import timezone
from intranet.models import DocumentoRestrito, CategoriaDocumento
from .forms import NoticiaForm, PopupForm, CategoriaDocForm, DocumentoForm
from noticias.models import Noticia
from core.models import ConfiguracaoHome
from programacao.models import AtividadeSemanal, Doutrinaria, CursoEvento
from .forms import AtividadeSemanalForm, DoutrinariaForm, CursoEventoForm

@login_required(login_url='/login/')
def dashboard(request):
    # Busca as 5 últimas notícias para mostrar no resumo
    ultimas_noticias = Noticia.objects.all().order_by('-data_publicacao')[:5]
    
    return render(request, 'painel/dashboard.html', {
        'ultimas_noticias': ultimas_noticias
    })

@login_required(login_url='/login/')
def criar_noticia(request):
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)
            
            if not noticia.slug:
                noticia.slug = slugify(noticia.titulo)
                
            noticia.save()
            return redirect('painel_home')
    else:
        # AQUI: Definimos "FEPI" como padrão, mas é editável
        form = NoticiaForm(initial={
            'data_publicacao': timezone.now().date(),
            'autor': 'FEPI' 
        })

    return render(request, 'painel/criar_noticia.html', {'form': form})

# 1. LISTAR (Abre a tabela)
@login_required(login_url='/login/')
def listar_noticias(request):
    # Pega todas as notícias, da mais nova para a mais antiga
    noticias = Noticia.objects.all().order_by('-data_publicacao')
    return render(request, 'painel/listar_noticias.html', {'noticias': noticias})

# 2. EDITAR (Abre o formulário preenchido)
@login_required(login_url='/login/')
def editar_noticia(request, noticia_id):
    # Tenta pegar a notícia pelo ID, se não achar, dá erro 404
    noticia = get_object_or_404(Noticia, id=noticia_id)
    
    if request.method == 'POST':
        # Carrega o form com os dados novos (request.POST) E os antigos (instance=noticia)
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            form.save() # O save aqui atualiza em vez de criar novo
            return redirect('listar_noticias')
    else:
        # Abre o formulário preenchido com os dados atuais
        form = NoticiaForm(instance=noticia)
    
    return render(request, 'painel/criar_noticia.html', {'form': form})

# 3. EXCLUIR
@login_required(login_url='/login/')
def deletar_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id=noticia_id)
    noticia.delete()
    return redirect('listar_noticias')

@login_required(login_url='/login/')
def gerenciar_popup(request):
    # Pega a configuração existente (Geralmente é a primeira e única linha da tabela)
    config = ConfiguracaoHome.objects.first()
    
    # Se por algum milagre não existir configuração ainda, cria uma vazia
    if not config:
        config = ConfiguracaoHome.objects.create()

    if request.method == 'POST':
        # Editamos a configuração existente (instance=config)
        form = PopupForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            return redirect('painel_home')
    else:
        form = PopupForm(instance=config)

    return render(request, 'painel/gerenciar_popup.html', {'form': form})

@login_required(login_url='/login/')
def listar_documentos(request):
    documentos = DocumentoRestrito.objects.all()
    return render(request, 'painel/listar_documentos.html', {'documentos': documentos})

@login_required(login_url='/login/')
def criar_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_documentos')
    else:
        form = DocumentoForm()
    return render(request, 'painel/form_documento.html', {'form': form, 'titulo': 'Novo Documento'})

@login_required(login_url='/login/')
def editar_documento(request, id):
    doc = get_object_or_404(DocumentoRestrito, id=id)
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            return redirect('listar_documentos')
    else:
        form = DocumentoForm(instance=doc)
    return render(request, 'painel/form_documento.html', {'form': form, 'titulo': 'Editar Documento'})

@login_required(login_url='/login/')
def excluir_documento(request, id):
    doc = get_object_or_404(DocumentoRestrito, id=id)
    if request.method == 'POST':
        doc.delete()
        return redirect('listar_documentos')
    return render(request, 'painel/confirmar_exclusao.html', {'objeto': doc.titulo, 'voltar_url': 'listar_documentos'})

# --- GESTÃO DE CATEGORIAS ---

@login_required(login_url='/login/')
def listar_categorias_doc(request):
    categorias = CategoriaDocumento.objects.all()
    # Formulário simples na mesma página para adicionar rápido
    if request.method == 'POST':
        form = CategoriaDocForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_categorias_doc')
    else:
        form = CategoriaDocForm()
        
    return render(request, 'painel/listar_categorias_doc.html', {'categorias': categorias, 'form': form})

@login_required(login_url='/login/')
def excluir_categoria_doc(request, id):
    cat = get_object_or_404(CategoriaDocumento, id=id)
    try:
        cat.delete()
    except:
        # Se tiver documentos vinculados, não deixa apagar (proteção do banco)
        pass 
    return redirect('listar_categorias_doc')

# --- CENTRAL DA PROGRAMAÇÃO (HUB) ---
def programacao_hub(request):
    # Adicionamos a pasta /programacao/ no caminho
    return render(request, 'painel/programacao/programacao_hub.html')

# --- 1. GESTÃO DE ATIVIDADES SEMANAIS ---
@login_required(login_url='/login/')
def listar_atividades(request):
    atividades = AtividadeSemanal.objects.all().order_by('dia', 'horario')
    return render(request, 'painel/programacao/listar_atividades.html', {'atividades': atividades})

@login_required(login_url='/login/')
def gerenciar_atividade(request, id=None):
    # Se tem ID, edita. Se não tem, cria nova.
    instancia = None
    if id:
        instancia = get_object_or_404(AtividadeSemanal, id=id)
    
    if request.method == 'POST':
        form = AtividadeSemanalForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('listar_atividades')
    else:
        form = AtividadeSemanalForm(instance=instancia)
    
    titulo = "Editar Atividade" if id else "Nova Atividade Semanal"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
def excluir_atividade(request, id):
    item = get_object_or_404(AtividadeSemanal, id=id)
    item.delete()
    return redirect('listar_atividades')

# --- 2. GESTÃO DE PALESTRAS (DOUTRINÁRIAS) ---
@login_required(login_url='/login/')
def listar_palestras(request):
    palestras = Doutrinaria.objects.all().order_by('-data_hora')
    return render(request, 'painel/programacao/listar_palestras.html', {'palestras': palestras})

@login_required(login_url='/login/')
def gerenciar_palestra(request, id=None):
    instancia = None
    if id:
        instancia = get_object_or_404(Doutrinaria, id=id)
    
    if request.method == 'POST':
        form = DoutrinariaForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('listar_palestras')
    else:
        form = DoutrinariaForm(instance=instancia)
    
    titulo = "Editar Palestra" if id else "Nova Palestra Pública"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
def excluir_palestra(request, id):
    item = get_object_or_404(Doutrinaria, id=id)
    item.delete()
    return redirect('listar_palestras')

# --- 3. GESTÃO DE CURSOS E EVENTOS ---
@login_required(login_url='/login/')
def listar_eventos(request):
    eventos = CursoEvento.objects.all().order_by('-data_evento')
    return render(request, 'painel/programacao/listar_eventos.html', {'eventos': eventos})

@login_required(login_url='/login/')
def gerenciar_evento(request, id=None):
    instancia = None
    if id:
        instancia = get_object_or_404(CursoEvento, id=id)
    
    if request.method == 'POST':
        form = CursoEventoForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('listar_eventos')
    else:
        form = CursoEventoForm(instance=instancia)
    
    titulo = "Editar Evento Especial" if id else "Novo Curso ou Evento"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
def excluir_evento(request, id):
    item = get_object_or_404(CursoEvento, id=id)
    item.delete()
    return redirect('listar_eventos')




