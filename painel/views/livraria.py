# painel/views/livraria.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
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
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    
    livros_list = Livro.objects.select_related('categoria').all().order_by('titulo')
    
    if query:
        livros_list = livros_list.filter(
            Q(titulo__icontains=query) | 
            Q(autor__icontains=query)
        )
    if categoria_id:
        livros_list = livros_list.filter(categoria_id=categoria_id)
        
    paginator = Paginator(livros_list, 15)
    page_number = request.GET.get('page')
    livros = paginator.get_page(page_number)
    
    categorias = CategoriaLivro.objects.all().order_by('nome')
    
    return render(request, 'painel/livraria/listar_livros.html', {
        'livros': livros,
        'query': query,
        'categoria_id': categoria_id,
        'categorias': categorias
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
            # Lemos os dados
            df = pd.read_excel(
                excel_file, 
                usecols=[0, 2, 4, 13, 14], 
                names=['codigo', 'descricao', 'preco', 'estoque', 'editora'],
                engine='openpyxl'
            )

            # Limpeza e Formatação
            df['codigo'] = df['codigo'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df['estoque'] = pd.to_numeric(df['estoque'], errors='coerce').fillna(0).astype(int)
            
            if df['preco'].dtype == object:
                df['preco'] = df['preco'].astype(str).str.replace('R$', '', regex=False)
                df['preco'] = df['preco'].str.replace('.', '', regex=False)
                df['preco'] = df['preco'].str.replace(',', '.', regex=False)
            df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0.0)

            # Filtra linhas vazias
            df = df[df['codigo'] != 'nan']
            df = df[df['codigo'] != '']

            codigos_planilha = df['codigo'].tolist()

            # Busca todos os produtos existentes DE UMA VEZ SÓ
            produtos_existentes = {
                p.codigo_barras: p 
                for p in ProdutoLivraria.objects.filter(codigo_barras__in=codigos_planilha)
            }

            produtos_para_criar = []
            produtos_para_atualizar = []

            for _, row in df.iterrows():
                codigo = row['codigo']
                descricao = str(row['descricao'])[:255]
                preco = row['preco']
                estoque = row['estoque']
                editora = str(row['editora'])[:100] if pd.notna(row['editora']) else ''

                if codigo in produtos_existentes:
                    p = produtos_existentes[codigo]
                    p.descricao = descricao
                    p.preco_venda = preco
                    p.quantidade_estoque = estoque
                    p.editora = editora
                    produtos_para_atualizar.append(p)
                else:
                    produtos_para_criar.append(
                        ProdutoLivraria(
                            codigo_barras=codigo,
                            descricao=descricao,
                            preco_venda=preco,
                            quantidade_estoque=estoque,
                            editora=editora
                        )
                    )

            # Transação Atômica e Processamento em Lote
            with transaction.atomic():
                if produtos_para_criar:
                    ProdutoLivraria.objects.bulk_create(produtos_para_criar, batch_size=500)
                if produtos_para_atualizar:
                    ProdutoLivraria.objects.bulk_update(
                        produtos_para_atualizar, 
                        ['descricao', 'preco_venda', 'quantidade_estoque', 'editora'], 
                        batch_size=500
                    )
                
            msg_sucesso = f'{len(produtos_para_criar)} novos itens criados e {len(produtos_para_atualizar)} atualizados.'
            messages.success(request, f'Fantástico! {msg_sucesso}')
            HistoricoUploadProdutos.objects.create(usuario=request.user, sucesso=True, mensagem=msg_sucesso)
            
        except Exception as e:
            msg_erro = f'Erro ao processar a planilha: {str(e)}'
            messages.error(request, msg_erro)
            HistoricoUploadProdutos.objects.create(usuario=request.user, sucesso=False, mensagem=msg_erro[:500])
            
        return redirect('livraria_hub') 

    # --- Busca os últimos 4 históricos para mandar para a tela ---
    ultimos_uploads = HistoricoUploadProdutos.objects.all()[:4]
    
    return render(request, 'painel/livraria/upload_planilha.html', {'historico': ultimos_uploads})