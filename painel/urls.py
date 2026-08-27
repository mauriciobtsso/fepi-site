# painel/urls.py
from django.urls import path
from . import views
from painel.views import ia_views, radar_views
from painel.views.site import config_email
from .views import blogs, noticias, upload_planilha_produtos

urlpatterns = [
    path('', views.dashboard, name='painel_home'),
    path('noticias/nova/', views.criar_noticia, name='criar_noticia'),
    
    # Rota da Inteligência Artificial
    path('api/assistente-ia/', ia_views.chat_assistente_ia, name='assistente_ia'),

    # --- NOTICIAS ---
    path('noticias/', views.listar_noticias, name='listar_noticias'),
    path('noticias/editar/<int:noticia_id>/', views.editar_noticia, name='editar_noticia'),
    path('noticias/deletar/<int:noticia_id>/', views.deletar_noticia, name='deletar_noticia'),
    path('popup/', views.gerenciar_popup, name='gerenciar_popup'),
    path('noticias/radar/', radar_views.radar_noticias, name='radar_noticias'),
    path('noticias/upload-editorjs/', noticias.upload_imagem_editorjs_custom, name='upload_editorjs_custom'),

    # Colunas
    path('colunas/', views.listar_colunas, name='listar_colunas'),
    path('colunas/nova/', views.criar_coluna, name='criar_coluna'),
    path('colunas/editar/<int:id>/', views.editar_coluna, name='editar_coluna'),
    path('colunas/excluir/<int:id>/', views.excluir_coluna, name='excluir_coluna'),

    # Documentos
    path('documentos/', views.listar_documentos, name='listar_documentos'),
    path('documentos/novo/', views.criar_documento, name='criar_documento'),
    path('documentos/editar/<int:id>/', views.editar_documento, name='editar_documento'),
    path('documentos/excluir/<int:id>/', views.excluir_documento, name='excluir_documento'),
    
    # Categorias Documentos
    path('documentos/categorias/', views.listar_categorias_doc, name='listar_categorias_doc'),
    path('documentos/categorias/excluir/<int:id>/', views.excluir_categoria_doc, name='excluir_categoria_doc'),
    
    # --- PROGRAMAÇÃO ---
    path('programacao/', views.programacao_hub, name='programacao_hub'),
    
    # Atividades Semanais
    path('programacao/atividades/', views.listar_atividades, name='listar_atividades'),
    path('programacao/atividades/nova/', views.gerenciar_atividade, name='nova_atividade'),
    path('programacao/atividades/editar/<int:id>/', views.gerenciar_atividade, name='editar_atividade'),
    path('programacao/atividades/excluir/<int:id>/', views.excluir_atividade, name='excluir_atividade'),

    # Palestras
    path('programacao/palestras/', views.listar_palestras, name='listar_palestras'),
    path('programacao/palestras/nova/', views.gerenciar_palestra, name='nova_palestra'),
    path('programacao/palestras/editar/<int:id>/', views.gerenciar_palestra, name='editar_palestra'),
    path('programacao/palestras/excluir/<int:id>/', views.excluir_palestra, name='excluir_palestra'),

    # Cursos/Eventos
    path('programacao/eventos/', views.listar_eventos, name='listar_eventos'),
    path('programacao/eventos/nova/', views.gerenciar_evento, name='novo_evento'),
    path('programacao/eventos/editar/<int:id>/', views.gerenciar_evento, name='editar_evento'),
    path('programacao/eventos/excluir/<int:id>/', views.excluir_evento, name='excluir_evento'),

    # --- LIVRARIA ---
    path('livraria/', views.livraria_hub, name='livraria_hub'),
    
    # Livros
    path('livraria/livros/', views.listar_livros, name='listar_livros'),
    path('livraria/livros/novo/', views.gerenciar_livro, name='novo_livro'),
    path('livraria/livros/editar/<int:id>/', views.gerenciar_livro, name='editar_livro'),
    path('livraria/livros/excluir/<int:id>/', views.excluir_livro, name='excluir_livro'),
    
    # Categorias Livraria
    path('livraria/categorias/', views.listar_categorias_liv, name='listar_categorias_liv'),
    path('livraria/categorias/excluir/<int:id>/', views.excluir_categoria_liv, name='excluir_categoria_liv'),

    # Configuração
    path('livraria/config/', views.config_livraria, name='config_livraria'),

    # ----------------------------------------------------------------------
    # ROTA DE IMPORTAÇÃO DA PLANILHA (ADICIONE ESTA LINHA)
    path('livraria/importar-produtos/', upload_planilha_produtos, name='upload_planilha_produtos'),
    # ----------------------------------------------------------------------

    # --- SITE E REDES ---
    path('site/', views.site_hub, name='site_hub'),
    path('site/email/', config_email, name='config_email'),
    
    # YouTube
    path('site/youtube/', views.config_youtube, name='config_youtube'),
    
    # Instagram (Vitrine)
    path('site/instagram/', views.listar_instagram, name='listar_instagram'),
    path('site/instagram/novo/', views.gerenciar_post_insta, name='novo_post_insta'),
    path('site/instagram/editar/<int:id>/', views.gerenciar_post_insta, name='editar_post_insta'),
    path('site/instagram/excluir/<int:id>/', views.excluir_post_insta, name='excluir_post_insta'),

    # --- SECRETARIA: EQUIPE E ESTRUTURA ---
    path('secretaria/equipe/', views.equipe_hub, name='equipe_hub'),
   
    # Membros
    path('secretaria/membro/novo/', views.gerenciar_membro, name='novo_membro'),
    path('secretaria/membro/editar/<int:id>/', views.gerenciar_membro, name='editar_membro'),
    path('secretaria/membro/excluir/<int:id>/', views.excluir_membro, name='excluir_membro'),
    
    # Departamentos
    path('secretaria/departamento/novo/', views.gerenciar_departamento, name='novo_departamento'),
    path('secretaria/departamento/editar/<int:id>/', views.gerenciar_departamento, name='editar_departamento'),
    path('secretaria/departamento/excluir/<int:id>/', views.excluir_departamento, name='excluir_departamento'),

    # Cargos
    path('secretaria/cargo/novo/', views.gerenciar_cargo, name='novo_cargo'),
    path('secretaria/cargo/editar/<int:id>/', views.gerenciar_cargo, name='editar_cargo'),
    path('secretaria/cargo/excluir/<int:id>/', views.excluir_cargo, name='excluir_cargo'),

    # --- SITE: INSTITUCIONAL ---
    path('site/institucional/', views.editar_institucional, name='editar_institucional'),
    path('site/contato/', views.editar_contato, name='editar_contato'),

    # --- CENTROS ESPÍRITAS ---
    path('secretaria/centros/', views.listar_centros, name='listar_centros'),
    path('secretaria/centros/novo/', views.gerenciar_centro, name='novo_centro'),
    path('secretaria/centros/editar/<int:id>/', views.gerenciar_centro, name='editar_centro'),
    path('secretaria/centros/excluir/<int:id>/', views.excluir_centro, name='excluir_centro'),

    # --- DOAÇÕES ---
    path('site/doacoes/', views.listar_doacoes, name='listar_doacoes'),
    path('site/doacoes/novo/', views.gerenciar_doacao, name='nova_doacao'),
    path('site/doacoes/editar/<int:id>/', views.gerenciar_doacao, name='editar_doacao'),
    path('site/doacoes/excluir/<int:id>/', views.excluir_doacao, name='excluir_doacao'),
    path('site/doacoes/config/', views.config_pagina_doacao, name='config_pagina_doacao'),

    # --- RECURSOS / DOWNLOADS ---
    path('site/recursos/', views.recursos_hub, name='recursos_hub'),
    # Itens
    path('site/recursos/novo/', views.gerenciar_recurso, name='novo_recurso'),
    path('site/recursos/editar/<int:id>/', views.gerenciar_recurso, name='editar_recurso'),
    path('site/recursos/excluir/<int:id>/', views.excluir_recurso, name='excluir_recurso'),
    # Seções
    path('site/recursos/secao/nova/', views.gerenciar_secao_recurso, name='nova_secao_recurso'),
    path('site/recursos/secao/editar/<int:id>/', views.gerenciar_secao_recurso, name='editar_secao_recurso'),
    path('site/recursos/secao/excluir/<int:id>/', views.excluir_secao_recurso, name='excluir_secao_recurso'),

    # --- FINANCEIRO / MENSALIDADES ---
    path('financeiro/', views.financeiro_hub, name='financeiro_hub'),
    path('financeiro/gateway/', views.gerenciar_configuracao_gateway, name='gerenciar_configuracao_gateway'),
    path('financeiro/planos/novo/', views.gerenciar_plano_financeiro, name='novo_plano_financeiro'),
    path('financeiro/planos/editar/<int:id>/', views.gerenciar_plano_financeiro, name='editar_plano_financeiro'),
    path('financeiro/adesoes/nova/', views.gerenciar_adesao_financeira, name='nova_adesao_financeira'),
    path('financeiro/adesoes/editar/<int:id>/', views.gerenciar_adesao_financeira, name='editar_adesao_financeira'),
    path('financeiro/cobrancas/nova/', views.gerenciar_cobranca_financeira, name='nova_cobranca_financeira'),
    path('financeiro/cobrancas/editar/<int:id>/', views.gerenciar_cobranca_financeira, name='editar_cobranca_financeira'),
    path('financeiro/auditoria/', views.listar_auditoria_financeira, name='listar_auditoria_financeira'),
    path('financeiro/relatorio/', views.relatorio_financeiro, name='relatorio_financeiro'),
    path('financeiro/manual/', views.manual_financeiro, name='manual_financeiro'),

    # --- ADMINISTRAÇÃO ---
    path('usuarios/', views.gerenciar_usuarios, name='gerenciar_usuarios'),
    path('usuarios/novo/', views.criar_usuario, name='criar_usuario'),
    path('usuarios/editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<int:id>/', views.excluir_usuario, name='excluir_usuario'),
    
    # Editar a Página "Seja Membro"
    path('usuarios/pagina-seja-membro/', views.editar_pagina_membro, name='editar_pagina_membro'),

    # --- SYSTEMA DE BLOGS DOS DEPARTAMENTOS ---
    path('blogs-departamentos/', views.blogs_hub, name='blogs_hub'),
    path('blogs-departamentos/post/novo/', views.gerenciar_post_blog, name='criar_post_blog'),
    path('blogs-departamentos/post/editar/<int:id>/', views.gerenciar_post_blog, name='editar_post_blog'),
    path('blogs-departamentos/post/excluir/<int:id>/', views.excluir_post_blog, name='excluir_post_blog'),
    path('blogs-departamentos/configurar/<int:depto_id>/', views.configurar_rede_social_blog, name='configurar_rede_social_blog'),
    path('blogs-departamentos/<int:depto_id>/membros/', views.gerenciar_membros_blog, name='gerenciar_membros_blog'),
    path('blogs-departamentos/membros/<int:id>/excluir/', views.excluir_membro_blog, name='excluir_membro_blog'),
    path('blogs-departamentos/excluir/<int:id>/', blogs.excluir_departamento_blog, name='excluir_departamento_blog'),
    path('blogs-departamentos/criar/', blogs.criar_departamento, name='painel_criar_departamento'),
    
    # 🏷️ NOVAS ROTAS: Gerenciamento do CRUD de Categorias do Blog
    path('blogs-departamentos/categorias/', views.listar_categorias_blog, name='listar_categorias_blog'),
    path('blogs-departamentos/categorias/nova/', views.gerenciar_categoria_blog, name='nova_categoria_blog'),
    path('blogs-departamentos/categorias/editar/<int:id>/', views.gerenciar_categoria_blog, name='editar_categoria_blog'),
    path('blogs-departamentos/categorias/excluir/<int:id>/', views.excluir_categoria_blog, name='excluir_categoria_blog'),
]