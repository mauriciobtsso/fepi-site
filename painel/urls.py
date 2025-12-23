from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='painel_home'),
    path('noticias/nova/', views.criar_noticia, name='criar_noticia'),

    # --- NOVAS ROTAS ---
    path('noticias/', views.listar_noticias, name='listar_noticias'),
    path('noticias/editar/<int:noticia_id>/', views.editar_noticia, name='editar_noticia'),
    path('noticias/deletar/<int:noticia_id>/', views.deletar_noticia, name='deletar_noticia'),
    path('popup/', views.gerenciar_popup, name='gerenciar_popup'),

    # Documentos
    path('documentos/', views.listar_documentos, name='listar_documentos'),
    path('documentos/novo/', views.criar_documento, name='criar_documento'),
    path('documentos/editar/<int:id>/', views.editar_documento, name='editar_documento'),
    path('documentos/excluir/<int:id>/', views.excluir_documento, name='excluir_documento'),
    
    # Categorias
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
    
    # Categorias
    path('livraria/categorias/', views.listar_categorias_liv, name='listar_categorias_liv'),
    path('livraria/categorias/excluir/<int:id>/', views.excluir_categoria_liv, name='excluir_categoria_liv'),

    # Configuração
    path('livraria/config/', views.config_livraria, name='config_livraria'),

    # --- SITE E REDES ---
    path('site/', views.site_hub, name='site_hub'),
    
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


]