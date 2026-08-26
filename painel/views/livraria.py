# painel/views/livraria.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal, InvalidOperation
import pandas as pd

from livraria.models import Livro, Categoria as CategoriaLivro, LivrariaConfig, ProdutoLivraria, HistoricoUploadProdutos
from painel.forms import LivroForm, CategoriaLivroForm, LivrariaConfigForm
from painel.views.auth import check_acesso_painel
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def livraria_hub(request):
    return render(request, 'painel/livraria/livraria_hub.html')

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def listar_livros(request):
    query = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()
    estoque_filtro = request.GET.get('estoque', '').strip()
    status_filtro = request.GET.get('status', '').strip()
    completude = request.GET.get('completude', '').strip()

    # Ações em lote: alteram somente flags administrativas, sem excluir registros.
    if request.method == 'POST':
        acao = request.POST.get('acao')
        ids = request.POST.getlist('livros')
        selecionados = Livro.objects.filter(id__in=ids)
        alterados = selecionados.count()
        if acao == 'ativar':
            selecionados.update(ativo_na_vitrine=True)
            messages.success(request, f'{alterados} livro(s) ativado(s) na vitrine.')
        elif acao == 'desativar':
            selecionados.update(ativo_na_vitrine=False)
            messages.success(request, f'{alterados} livro(s) desativado(s) da vitrine.')
        elif acao == 'disponivel':
            selecionados.filter(quantidade_estoque__gt=0).update(disponivel=True)
            messages.success(request, 'Disponibilidade atualizada para os livros com estoque.')
        elif acao == 'indisponivel':
            selecionados.update(disponivel=False)
            messages.success(request, f'{alterados} livro(s) marcado(s) como indisponível(is).')
        else:
            messages.warning(request, 'Selecione uma ação válida.')
        return redirect(request.get_full_path())

    livros_list = Livro.objects.select_related('categoria').all().order_by('titulo')
    if query:
        livros_list = livros_list.filter(Q(titulo__icontains=query) | Q(autor__icontains=query) | Q(codigo__icontains=query))
    if categoria_id:
        livros_list = livros_list.filter(categoria_id=categoria_id)
    if estoque_filtro == 'positivo':
        livros_list = livros_list.filter(quantidade_estoque__gt=0)
    elif estoque_filtro == 'zero':
        livros_list = livros_list.filter(quantidade_estoque=0)
    if status_filtro == 'ativo':
        livros_list = livros_list.filter(ativo_na_vitrine=True)
    elif status_filtro == 'inativo':
        livros_list = livros_list.filter(ativo_na_vitrine=False)
    elif status_filtro == 'disponivel':
        livros_list = livros_list.filter(disponivel=True)
    elif status_filtro == 'indisponivel':
        livros_list = livros_list.filter(disponivel=False)
    if completude == 'incompleto':
        livros_list = livros_list.filter(Q(capa='') | Q(capa__isnull=True) | Q(autor='') | Q(autor='A preencher') | Q(categoria__isnull=True))

    paginator = Paginator(livros_list, 30)
    livros = paginator.get_page(request.GET.get('page'))
    categorias = CategoriaLivro.objects.all().order_by('nome')

    return render(request, 'painel/livraria/listar_livros.html', {
        'livros': livros,
        'query': query,
        'categoria_id': categoria_id,
        'categorias': categorias,
        'estoque_filtro': estoque_filtro,
        'status_filtro': status_filtro,
        'completude': completude,
    })

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
def upload_planilha_produtos(request):
    if request.method == 'POST' and request.FILES.get('planilha'):
        excel_file = request.FILES['planilha']
        
        if not excel_file.name.endswith('.xlsx'):
            msg_erro = 'Por favor, envie um arquivo .xlsx válido.'
            messages.error(request, msg_erro)
            HistoricoUploadProdutos.objects.create(usuario=request.user, sucesso=False, mensagem=msg_erro)
            return redirect('upload_planilha_produtos')

        try:
            df = pd.read_excel(
                excel_file,
                usecols=[0, 2, 4, 13, 14],
                names=['codigo', 'descricao', 'preco', 'estoque', 'editora'],
                engine='openpyxl'
            )

            # Normaliza os campos operacionais importados.
            df['codigo'] = df['codigo'].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df['descricao'] = df['descricao'].fillna('').astype(str).str.strip()
            df['editora'] = df['editora'].fillna('').astype(str).str.strip().str[:100]
            df['estoque'] = pd.to_numeric(df['estoque'], errors='coerce').fillna(0).clip(lower=0).astype(int)

            def converter_preco(valor):
                if pd.isna(valor):
                    return Decimal('0.00')
                texto = str(valor).strip().replace('R$', '').replace(' ', '')
                # Trata tanto 1.234,56 quanto 1234.56 sem deslocar a casa decimal.
                if ',' in texto:
                    texto = texto.replace('.', '').replace(',', '.')
                try:
                    return Decimal(texto).quantize(Decimal('0.01'))
                except (InvalidOperation, ValueError):
                    return Decimal('0.00')

            df['preco'] = df['preco'].apply(converter_preco)
            df = df[(df['codigo'] != '') & (df['descricao'] != '')]
            # Em caso de código repetido, vale a última ocorrência da planilha.
            df = df.drop_duplicates(subset=['codigo'], keep='last')
            codigos_planilha = df['codigo'].tolist()
            agora = timezone.now()

            produtos_existentes = {
                p.codigo_barras: p
                for p in ProdutoLivraria.objects.filter(codigo_barras__in=codigos_planilha)
            }
            livros_existentes = {
                l.codigo: l
                for l in Livro.objects.filter(codigo__in=codigos_planilha)
            }

            produtos_para_criar = []
            produtos_para_atualizar = []
            livros_para_criar = []
            livros_para_atualizar = []
            novos_livros = 0
            livros_atualizados = 0
            estoque_zero = 0

            for _, row in df.iterrows():
                codigo = row['codigo']
                descricao = row['descricao'][:255]
                preco = row['preco']
                estoque = int(row['estoque'])
                editora = row['editora']

                produto = produtos_existentes.get(codigo)
                if produto:
                    produto.descricao = descricao
                    produto.preco_venda = preco
                    produto.quantidade_estoque = estoque
                    produto.editora = editora
                    produtos_para_atualizar.append(produto)
                else:
                    produtos_para_criar.append(ProdutoLivraria(
                        codigo_barras=codigo,
                        descricao=descricao,
                        preco_venda=preco,
                        quantidade_estoque=estoque,
                        editora=editora,
                    ))

                livro = livros_existentes.get(codigo)
                if livro:
                    # Atualiza somente dados vindos da planilha. Capa, sinopse,
                    # autor, categoria, ativação e destaque permanecem manuais.
                    livro.titulo = descricao
                    livro.preco = preco
                    livro.quantidade_estoque = estoque
                    livro.ultima_sincronizacao = agora
                    if estoque == 0:
                        livro.disponivel = False
                        estoque_zero += 1
                    livros_para_atualizar.append(livro)
                    livros_atualizados += 1
                else:
                    slug_base = slugify(descricao)[:220] or 'livro'
                    slug_codigo = slugify(codigo) or 'item'
                    livros_para_criar.append(Livro(
                        codigo=codigo,
                        titulo=descricao,
                        slug=f'{slug_base}-{slug_codigo}'[:255],
                        autor='A preencher',
                        preco=preco,
                        quantidade_estoque=estoque,
                        ultima_sincronizacao=agora,
                        ativo_na_vitrine=False,
                        # Estoque positivo sugere disponibilidade; a publicação
                        # continua sempre inativa até revisão do administrador.
                        disponivel=estoque > 0,
                    ))
                    novos_livros += 1
                    if estoque == 0:
                        estoque_zero += 1

            with transaction.atomic():
                if produtos_para_criar:
                    ProdutoLivraria.objects.bulk_create(produtos_para_criar, batch_size=500)
                if produtos_para_atualizar:
                    ProdutoLivraria.objects.bulk_update(
                        produtos_para_atualizar,
                        ['descricao', 'preco_venda', 'quantidade_estoque', 'editora'],
                        batch_size=500,
                    )
                if livros_para_criar:
                    Livro.objects.bulk_create(livros_para_criar, batch_size=500)
                if livros_para_atualizar:
                    Livro.objects.bulk_update(
                        livros_para_atualizar,
                        ['titulo', 'preco', 'quantidade_estoque', 'ultima_sincronizacao', 'disponivel'],
                        batch_size=500,
                    )

            msg_sucesso = (
                f'{novos_livros} novos livros criados, {livros_atualizados} livros atualizados; '
                f'{len(produtos_para_criar)} produtos de estoque criados e '
                f'{len(produtos_para_atualizar)} atualizados. '
                f'{estoque_zero} item(ns) marcado(s) como indisponível(is). '
                'Novos livros entram inativos e aguardam revisão da vitrine.'
            )
            messages.success(request, f'Importação concluída! {msg_sucesso}')
            HistoricoUploadProdutos.objects.create(usuario=request.user, sucesso=True, mensagem=msg_sucesso)

        except Exception as e:
            msg_erro = f'Erro ao processar a planilha: {str(e)}'
            messages.error(request, msg_erro)
            HistoricoUploadProdutos.objects.create(usuario=request.user, sucesso=False, mensagem=msg_erro[:500])
            
        return redirect('livraria_hub') 

    # --- Busca os últimos 4 históricos para mandar para a tela ---
    ultimos_uploads = HistoricoUploadProdutos.objects.all()[:4]
    
    return render(request, 'painel/livraria/upload_planilha.html', {'historico': ultimos_uploads})