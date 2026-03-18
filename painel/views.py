from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.utils import timezone
from intranet.models import DocumentoRestrito, CategoriaDocumento
from .forms import NoticiaForm, PopupForm, CategoriaDocForm, DocumentoForm, CargoForm, TipoDiretoriaForm, MembroDiretoriaForm, PaginaInstitucionalForm
from noticias.models import Noticia
from core.models import ConfiguracaoHome, ConfiguracaoYouTube, PostInstagram, Cargo, TipoDiretoria, MembroDiretoria, PaginaInstitucional
from programacao.models import AtividadeSemanal, Doutrinaria, CursoEvento
from .forms import AtividadeSemanalForm, DoutrinariaForm, CursoEventoForm, YoutubeConfigForm, PostInstagramForm
from livraria.models import Livro, Categoria as CategoriaLivro, LivrariaConfig
from .forms import LivroForm, CategoriaLivroForm, LivrariaConfigForm, CentroForm, FormaDoacaoForm, SecaoLinkForm, LinkItemForm
from centros.models import Centro
from doacoes.models import FormaDoacao
from recursos.models import SecaoLink, LinkItem

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

# --- HUB DA LIVRARIA ---
@login_required(login_url='/login/')
def livraria_hub(request):
    return render(request, 'painel/livraria/livraria_hub.html')

# --- 1. GESTÃO DE LIVROS ---
@login_required(login_url='/login/')
def listar_livros(request):
    livros = Livro.objects.select_related('categoria').all().order_by('titulo')
    return render(request, 'painel/livraria/listar_livros.html', {'livros': livros})

@login_required(login_url='/login/')
def gerenciar_livro(request, id=None):
    instancia = get_object_or_404(Livro, id=id) if id else None
    
    if request.method == 'POST':
        form = LivroForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('listar_livros')
    else:
        form = LivroForm(instance=instancia)
    
    # Reutilizando o template bonito que fizemos antes!
    titulo = "Editar Livro" if id else "Novo Livro"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
def excluir_livro(request, id):
    livro = get_object_or_404(Livro, id=id)
    livro.delete()
    return redirect('listar_livros')

# --- 2. GESTÃO DE CATEGORIAS (LIVRARIA) ---
@login_required(login_url='/login/')
def listar_categorias_liv(request):
    categorias = CategoriaLivro.objects.all()
    # Formulário Rápido na mesma página
    if request.method == 'POST':
        form = CategoriaLivroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_categorias_liv')
    else:
        form = CategoriaLivroForm()
        
    return render(request, 'painel/livraria/listar_categorias.html', {'categorias': categorias, 'form': form})

@login_required(login_url='/login/')
def excluir_categoria_liv(request, id):
    cat = get_object_or_404(CategoriaLivro, id=id)
    # Evita apagar se tiver livros
    if not cat.livro_set.exists():
        cat.delete()
    return redirect('listar_categorias_liv')

# --- 3. CONFIGURAÇÃO (LOGO/INSTA) ---
@login_required(login_url='/login/')
def config_livraria(request):
    # Pega o primeiro registro ou cria se não existir (Singleton)
    config, created = LivrariaConfig.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        form = LivrariaConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            return redirect('livraria_hub')
    else:
        form = LivrariaConfigForm(instance=config)
        
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': 'Configuração da Livraria'})

# --- HUB DE GESTÃO DO SITE ---
@login_required(login_url='/login/')
def site_hub(request):
    return render(request, 'painel/site/site_hub.html')

# --- 1. CONFIGURAÇÃO DO YOUTUBE ---
@login_required(login_url='/login/')
def config_youtube(request):
    # Pega a primeira configuração ou cria (Singleton)
    config, created = ConfiguracaoYouTube.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        form = YoutubeConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            return redirect('site_hub')
    else:
        form = YoutubeConfigForm(instance=config)
        
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': 'Destaque do YouTube'})

# --- 2. VITRINE DO INSTAGRAM ---
@login_required(login_url='/login/')
def listar_instagram(request):
    posts = PostInstagram.objects.all().order_by('-data_post')
    return render(request, 'painel/site/listar_instagram.html', {'posts': posts})

@login_required(login_url='/login/')
def gerenciar_post_insta(request, id=None):
    post = get_object_or_404(PostInstagram, id=id) if id else None
    
    if request.method == 'POST':
        form = PostInstagramForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('listar_instagram')
    else:
        form = PostInstagramForm(instance=post)
        
    titulo = "Editar Post da Vitrine" if id else "Novo Post da Vitrine"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
def excluir_post_insta(request, id):
    post = get_object_or_404(PostInstagram, id=id)
    post.delete()
    return redirect('listar_instagram')

# --- HUB DE GESTÃO DE EQUIPE ---
@login_required(login_url='/login/')
def equipe_hub(request):
    membros = MembroDiretoria.objects.all().order_by('tipo__ordem', 'ordem')
    departamentos = TipoDiretoria.objects.all().order_by('ordem')
    cargos = Cargo.objects.all().order_by('nome')
    return render(request, 'painel/secretaria/equipe_hub.html', {
        'membros': membros,
        'departamentos': departamentos,
        'cargos': cargos
    })

# --- GENÉRICOS PARA EQUIPE (Adicionar/Editar/Excluir) ---

# 1. Membros
@login_required(login_url='/login/')
def gerenciar_membro(request, id=None):
    instancia = get_object_or_404(MembroDiretoria, id=id) if id else None
    if request.method == 'POST':
        form = MembroDiretoriaForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('equipe_hub')
    else:
        form = MembroDiretoriaForm(instance=instancia)
    titulo = "Editar Membro" if id else "Novo Membro da Diretoria"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
def excluir_membro(request, id):
    get_object_or_404(MembroDiretoria, id=id).delete()
    return redirect('equipe_hub')

# 2. Departamentos (Tipos)
@login_required(login_url='/login/')
def gerenciar_departamento(request, id=None):
    instancia = get_object_or_404(TipoDiretoria, id=id) if id else None
    if request.method == 'POST':
        form = TipoDiretoriaForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('equipe_hub')
    else:
        form = TipoDiretoriaForm(instance=instancia)
    titulo = "Editar Departamento" if id else "Novo Departamento"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
def excluir_departamento(request, id):
    get_object_or_404(TipoDiretoria, id=id).delete()
    return redirect('equipe_hub')

# 3. Cargos
@login_required(login_url='/login/')
def gerenciar_cargo(request, id=None):
    instancia = get_object_or_404(Cargo, id=id) if id else None
    if request.method == 'POST':
        form = CargoForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('equipe_hub')
    else:
        form = CargoForm(instance=instancia)
    titulo = "Editar Cargo" if id else "Novo Cargo"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
def excluir_cargo(request, id):
    # Proteção: só apaga se não tiver membro vinculado
    cargo = get_object_or_404(Cargo, id=id)
    if not cargo.membrodiretoria_set.exists():
        cargo.delete()
    return redirect('equipe_hub')

# --- PÁGINA INSTITUCIONAL (TEXTO) ---
@login_required(login_url='/login/')
def editar_institucional(request):
    pagina, created = PaginaInstitucional.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = PaginaInstitucionalForm(request.POST, instance=pagina)
        if form.is_valid():
            form.save()
            return redirect('site_hub') # Volta para o hub do site
    else:
        form = PaginaInstitucionalForm(instance=pagina)
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': 'Editar Página Institucional'})

# --- 1. GESTÃO DE CENTROS ESPÍRITAS ---
@login_required(login_url='/login/')
def listar_centros(request):
    centros = Centro.objects.all().order_by('cidade', 'nome')
    return render(request, 'painel/secretaria/listar_centros.html', {'centros': centros})

@login_required(login_url='/login/')
def gerenciar_centro(request, id=None):
    instancia = get_object_or_404(Centro, id=id) if id else None
    if request.method == 'POST':
        form = CentroForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('listar_centros')
    else:
        form = CentroForm(instance=instancia)
    titulo = "Editar Centro Espírita" if id else "Novo Centro Espírita"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
def excluir_centro(request, id):
    get_object_or_404(Centro, id=id).delete()
    return redirect('listar_centros')

# --- 2. GESTÃO DE DOAÇÕES ---
@login_required(login_url='/login/')
def listar_doacoes(request):
    doacoes = FormaDoacao.objects.all().order_by('ordem')
    return render(request, 'painel/site/listar_doacoes.html', {'doacoes': doacoes})

@login_required(login_url='/login/')
def gerenciar_doacao(request, id=None):
    instancia = get_object_or_404(FormaDoacao, id=id) if id else None
    if request.method == 'POST':
        form = FormaDoacaoForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('listar_doacoes')
    else:
        form = FormaDoacaoForm(instance=instancia)
    titulo = "Editar Forma de Doação" if id else "Nova Forma de Doação"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
def excluir_doacao(request, id):
    get_object_or_404(FormaDoacao, id=id).delete()
    return redirect('listar_doacoes')

# --- 3. GESTÃO DE RECURSOS (DOWNLOADS) ---
@login_required(login_url='/login/')
def recursos_hub(request):
    secoes = SecaoLink.objects.all().order_by('ordem')
    itens = LinkItem.objects.all().select_related('secao').order_by('secao__ordem', 'titulo')
    return render(request, 'painel/site/recursos_hub.html', {'secoes': secoes, 'itens': itens})

# Link Item (Arquivo/Link)
@login_required(login_url='/login/')
def gerenciar_recurso(request, id=None):
    instancia = get_object_or_404(LinkItem, id=id) if id else None
    if request.method == 'POST':
        form = LinkItemForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('recursos_hub')
    else:
        form = LinkItemForm(instance=instancia)
    titulo = "Editar Recurso/Link" if id else "Novo Recurso/Link"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
def excluir_recurso(request, id):
    get_object_or_404(LinkItem, id=id).delete()
    return redirect('recursos_hub')

# Seção de Links (Categoria)
@login_required(login_url='/login/')
def gerenciar_secao_recurso(request, id=None):
    instancia = get_object_or_404(SecaoLink, id=id) if id else None
    if request.method == 'POST':
        form = SecaoLinkForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('recursos_hub')
    else:
        form = SecaoLinkForm(instance=instancia)
    titulo = "Editar Seção de Recursos" if id else "Nova Seção"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
def excluir_secao_recurso(request, id):
    secao = get_object_or_404(SecaoLink, id=id)
    secao.delete() # Cuidado: Apaga os links filhos em cascata
    return redirect('recursos_hub')



