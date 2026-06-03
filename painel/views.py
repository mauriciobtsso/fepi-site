from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction

# --- IMPORTS DE MODELS ---
from noticias.models import Noticia
from core.models import ConfiguracaoHome, ConfiguracaoYouTube, PostInstagram, Cargo, TipoDiretoria, MembroDiretoria, PaginaInstitucional, Coluna
from intranet.models import DocumentoRestrito, CategoriaDocumento
from programacao.models import AtividadeSemanal, Doutrinaria, CursoEvento
from livraria.models import Livro, Categoria as CategoriaLivro, LivrariaConfig
from centros.models import Centro
from doacoes.models import FormaDoacao
from recursos.models import SecaoLink, LinkItem
from usuarios.models import Perfil

# --- IMPORTS DE FORMS ---
from .forms import (
    NoticiaForm, PopupForm, CategoriaDocForm, DocumentoForm, CargoForm, 
    TipoDiretoriaForm, MembroDiretoriaForm, PaginaInstitucionalForm, 
    AtividadeSemanalForm, DoutrinariaForm, CursoEventoForm, YoutubeConfigForm, 
    PostInstagramForm, LivroForm, CategoriaLivroForm, LivrariaConfigForm, 
    CentroForm, FormaDoacaoForm, SecaoLinkForm, LinkItemForm, PerfilForm, ColunaForm
)

# --- BLINDAGEM DE ACESSO AO PAINEL ---
def check_acesso_painel(user):
    if user.is_superuser:
        return True
    if hasattr(user, 'perfil') and user.perfil.is_colunista and user.perfil.status == 'APROVADO':
        return True
    return False

def is_admin(user):
    return user.is_superuser

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def dashboard(request):
    ultimas_noticias = Noticia.objects.all().order_by('-data_publicacao')[:5]
    return render(request, 'painel/dashboard.html', {'ultimas_noticias': ultimas_noticias})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
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
        form = NoticiaForm(initial={'data_publicacao': timezone.now().date(), 'autor': 'FEPI'})
    return render(request, 'painel/criar_noticia.html', {'form': form})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_noticias(request):
    noticias = Noticia.objects.all().order_by('-data_publicacao')
    return render(request, 'painel/listar_noticias.html', {'noticias': noticias})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def editar_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id=noticia_id)
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            form.save()
            return redirect('listar_noticias')
    else:
        form = NoticiaForm(instance=noticia)
    return render(request, 'painel/criar_noticia.html', {'form': form})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def deletar_noticia(request, noticia_id):
    noticia = get_object_or_404(Noticia, id=noticia_id)
    noticia.delete()
    return redirect('listar_noticias')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_popup(request):
    config = ConfiguracaoHome.objects.first()
    if not config:
        config = ConfiguracaoHome.objects.create()
    if request.method == 'POST':
        form = PopupForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            return redirect('painel_home')
    else:
        form = PopupForm(instance=config)
    return render(request, 'painel/gerenciar_popup.html', {'form': form})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_documentos(request):
    documentos = DocumentoRestrito.objects.all()
    return render(request, 'painel/listar_documentos.html', {'documentos': documentos})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
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
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
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
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_documento(request, id):
    doc = get_object_or_404(DocumentoRestrito, id=id)
    if request.method == 'POST':
        doc.delete()
        return redirect('listar_documentos')
    return render(request, 'painel/confirmar_exclusao.html', {'objeto': doc.titulo, 'voltar_url': 'listar_documentos'})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_categorias_doc(request):
    categorias = CategoriaDocumento.objects.all()
    if request.method == 'POST':
        form = CategoriaDocForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_categorias_doc')
    else:
        form = CategoriaDocForm()
    return render(request, 'painel/listar_categorias_doc.html', {'categorias': categorias, 'form': form})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_categoria_doc(request, id):
    cat = get_object_or_404(CategoriaDocumento, id=id)
    try:
        cat.delete()
    except:
        pass 
    return redirect('listar_categorias_doc')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def programacao_hub(request):
    return render(request, 'painel/programacao/programacao_hub.html')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_atividades(request):
    atividades = AtividadeSemanal.objects.all().order_by('dia', 'horario')
    return render(request, 'painel/programacao/listar_atividades.html', {'atividades': atividades})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_atividade(request, id=None):
    instancia = get_object_or_404(AtividadeSemanal, id=id) if id else None
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
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_atividade(request, id):
    item = get_object_or_404(AtividadeSemanal, id=id)
    item.delete()
    return redirect('listar_atividades')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_palestras(request):
    palestras = Doutrinaria.objects.all().order_by('-data_hora')
    return render(request, 'painel/programacao/listar_palestras.html', {'palestras': palestras})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_palestra(request, id=None):
    instancia = get_object_or_404(Doutrinaria, id=id) if id else None
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
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_palestra(request, id):
    item = get_object_or_404(Doutrinaria, id=id)
    item.delete()
    return redirect('listar_palestras')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_eventos(request):
    eventos = CursoEvento.objects.all().order_by('-data_evento')
    return render(request, 'painel/programacao/listar_eventos.html', {'eventos': eventos})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_evento(request, id=None):
    instancia = get_object_or_404(CursoEvento, id=id) if id else None
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
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_evento(request, id):
    item = get_object_or_404(CursoEvento, id=id)
    item.delete()
    return redirect('listar_eventos')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def livraria_hub(request):
    return render(request, 'painel/livraria/livraria_hub.html')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_livros(request):
    livros = Livro.objects.select_related('categoria').all().order_by('titulo')
    return render(request, 'painel/livraria/listar_livros.html', {'livros': livros})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def gerenciar_livro(request, id=None):
    instancia = get_object_or_404(Livro, id=id) if id else None
    if request.method == 'POST':
        form = LivroForm(request.POST, request.FILES, instance=instancia)
        if form.is_valid():
            form.save()
            return redirect('listar_livros')
    else:
        form = LivroForm(instance=instancia)
    titulo = "Editar Livro" if id else "Novo Livro"
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_livro(request, id):
    livro = get_object_or_404(Livro, id=id)
    livro.delete()
    return redirect('listar_livros')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_categorias_liv(request):
    categorias = CategoriaLivro.objects.all()
    if request.method == 'POST':
        form = CategoriaLivroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_categorias_liv')
    else:
        form = CategoriaLivroForm()
    return render(request, 'painel/livraria/listar_categorias.html', {'categorias': categorias, 'form': form})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_categoria_liv(request, id):
    cat = get_object_or_404(CategoriaLivro, id=id)
    if not cat.livro_set.exists():
        cat.delete()
    return redirect('listar_categorias_liv')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def config_livraria(request):
    config, created = LivrariaConfig.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = LivrariaConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            return redirect('livraria_hub')
    else:
        form = LivrariaConfigForm(instance=config)
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': 'Configuração da Livraria'})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def site_hub(request):
    return render(request, 'painel/site/site_hub.html')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def config_youtube(request):
    config, created = ConfiguracaoYouTube.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = YoutubeConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            return redirect('site_hub')
    else:
        form = YoutubeConfigForm(instance=config)
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': 'Destaque do YouTube'})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_instagram(request):
    posts = PostInstagram.objects.all().order_by('-data_post')
    return render(request, 'painel/site/listar_instagram.html', {'posts': posts})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
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
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_post_insta(request, id):
    post = get_object_or_404(PostInstagram, id=id)
    post.delete()
    return redirect('listar_instagram')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def equipe_hub(request):
    membros = MembroDiretoria.objects.all().order_by('tipo__ordem', 'ordem')
    departamentos = TipoDiretoria.objects.all().order_by('ordem')
    cargos = Cargo.objects.all().order_by('nome')
    return render(request, 'painel/secretaria/equipe_hub.html', {
        'membros': membros,
        'departamentos': departamentos,
        'cargos': cargos
    })

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
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
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_membro(request, id):
    get_object_or_404(MembroDiretoria, id=id).delete()
    return redirect('equipe_hub')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
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
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_departamento(request, id):
    get_object_or_404(TipoDiretoria, id=id).delete()
    return redirect('equipe_hub')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
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
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_cargo(request, id):
    cargo = get_object_or_404(Cargo, id=id)
    if not cargo.membrodiretoria_set.exists():
        cargo.delete()
    return redirect('equipe_hub')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def editar_institucional(request):
    pagina, created = PaginaInstitucional.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = PaginaInstitucionalForm(request.POST, instance=pagina)
        if form.is_valid():
            form.save()
            return redirect('site_hub')
    else:
        form = PaginaInstitucionalForm(instance=pagina)
    return render(request, 'painel/programacao/form_generico.html', {'form': form, 'titulo': 'Editar Página Institucional'})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_centros(request):
    centros = Centro.objects.all().order_by('cidade', 'nome')
    return render(request, 'painel/secretaria/listar_centros.html', {'centros': centros})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
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
    # AQUI ESTÁ A CORREÇÃO! APONTANDO PARA O ARQUIVO CORRETO:
    return render(request, 'painel/secretaria/form_centro.html', {'form': form, 'titulo': titulo})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_centro(request, id):
    get_object_or_404(Centro, id=id).delete()
    return redirect('listar_centros')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_doacoes(request):
    doacoes = FormaDoacao.objects.all().order_by('ordem')
    return render(request, 'painel/site/listar_doacoes.html', {'doacoes': doacoes})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
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
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_doacao(request, id):
    get_object_or_404(FormaDoacao, id=id).delete()
    return redirect('listar_doacoes')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def recursos_hub(request):
    secoes = SecaoLink.objects.all().order_by('ordem')
    itens = LinkItem.objects.all().select_related('secao').order_by('secao__ordem', 'titulo')
    return render(request, 'painel/site/recursos_hub.html', {'secoes': secoes, 'itens': itens})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
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
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_recurso(request, id):
    get_object_or_404(LinkItem, id=id).delete()
    return redirect('recursos_hub')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
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
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_secao_recurso(request, id):
    secao = get_object_or_404(SecaoLink, id=id)
    secao.delete()
    return redirect('recursos_hub')


# --- ADMINISTRAÇÃO: GESTÃO DE USUÁRIOS E PERFIS ---
@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/painel/')
def gerenciar_usuarios(request):
    for su in User.objects.filter(is_superuser=True):
        Perfil.objects.get_or_create(
            user=su, 
            defaults={'nome_razao_social': 'Administrador do Sistema', 'tipo': 'PF', 'status': 'APROVADO'}
        )

    perfis = Perfil.objects.all().order_by('-id')
    
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
        
        status = request.POST.get('status', 'APROVADO')
        is_active = True if status == 'APROVADO' else False

        try:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Este nome de usuário já está em uso.")
                return render(request, 'painel/usuarios/form_usuario.html', {'titulo': 'Novo Usuário'})

            with transaction.atomic():
                user = User.objects.create_user(username=username, email=email, password=senha, is_active=is_active)
                
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
                perfil.save()

            messages.success(request, f"Usuário {username} criado com sucesso!")
            return redirect('gerenciar_usuarios')
        except Exception as e:
            messages.error(request, f"Erro ao criar usuário: {str(e)}")
            
    return render(request, 'painel/usuarios/form_usuario.html', {'titulo': 'Novo Usuário'})

@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/painel/')
def editar_usuario(request, id):
    perfil = get_object_or_404(Perfil, id=id)
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
        
        novo_status = request.POST.get('status')
        if novo_status:
            perfil.status = novo_status
            perfil.user.is_active = (novo_status == 'APROVADO')
        
        nova_senha = request.POST.get('nova_senha')
        if nova_senha:
            perfil.user.set_password(nova_senha)
            messages.info(request, "A senha do usuário foi redefinida.")

        email = request.POST.get('email')
        if email:
            perfil.user.email = email
            
        perfil.user.save()
        perfil.save()
        
        messages.success(request, f"Dados de {perfil.user.username} atualizados com sucesso!")
        return redirect('gerenciar_usuarios')
        
    return render(request, 'painel/usuarios/form_usuario.html', {'perfil': perfil, 'titulo': f'Editar Usuário: {perfil.user.username}'})

@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/painel/')
def excluir_usuario(request, id):
    perfil = get_object_or_404(Perfil, id=id)
    if perfil.user == request.user:
        messages.error(request, "Segurança: Você não pode excluir sua própria conta por aqui.")
        return redirect('gerenciar_usuarios')
        
    usuario = perfil.user
    usuario.delete()
    messages.success(request, "Usuário excluído permanentemente.")
    return redirect('gerenciar_usuarios')

# --- GESTÃO DE COLUNAS ---
@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_colunas(request):
    colunas = Coluna.objects.all().order_by('-data_publicacao')
    return render(request, 'painel/colunas/listar_colunas.html', {'colunas': colunas})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def criar_coluna(request):
    if request.method == 'POST':
        form = ColunaForm(request.POST, request.FILES)
        if form.is_valid():
            coluna = form.save(commit=False)
            if not coluna.slug:
                coluna.slug = slugify(coluna.titulo)
            coluna.save()
            messages.success(request, "Artigo criado com sucesso!")
            return redirect('listar_colunas')
    else:
        form = ColunaForm(initial={'data_publicacao': timezone.now()})
    return render(request, 'painel/colunas/criar_coluna.html', {'form': form, 'titulo': 'Escrever Artigo'})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def editar_coluna(request, id):
    coluna = get_object_or_404(Coluna, id=id)
    if request.method == 'POST':
        form = ColunaForm(request.POST, request.FILES, instance=coluna)
        if form.is_valid():
            form.save()
            messages.success(request, "Artigo atualizado!")
            return redirect('listar_colunas')
    else:
        form = ColunaForm(instance=coluna)
    return render(request, 'painel/colunas/criar_coluna.html', {'form': form, 'titulo': 'Editar Artigo'})

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def excluir_coluna(request, id):
    coluna = get_object_or_404(Coluna, id=id)
    coluna.delete()
    messages.success(request, "Artigo excluído.")
    return redirect('listar_colunas')