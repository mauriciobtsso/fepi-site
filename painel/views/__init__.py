# painel/views/__init__.py

from .auth import check_acesso_painel, is_admin
from .dashboard import dashboard
from .noticias import criar_noticia, listar_noticias, editar_noticia, deletar_noticia
from .site import site_hub, gerenciar_popup, config_youtube, listar_instagram, gerenciar_post_insta, excluir_post_insta, editar_contato, editar_institucional
from .intranet import listar_documentos, criar_documento, editar_documento, excluir_documento, listar_categorias_doc, excluir_categoria_doc
from .programacao import programacao_hub, listar_atividades, gerenciar_atividade, excluir_atividade, listar_palestras, gerenciar_palestra, excluir_palestra, listar_eventos, gerenciar_evento, excluir_evento
from .livraria import livraria_hub, listar_livros, gerenciar_livro, excluir_livro, listar_categorias_liv, excluir_categoria_liv, config_livraria, upload_planilha_produtos
from .equipe import equipe_hub, gerenciar_membro, excluir_membro, gerenciar_departamento, excluir_departamento, gerenciar_cargo, excluir_cargo
from .centros import listar_centros, gerenciar_centro, excluir_centro
from .doacoes import listar_doacoes, gerenciar_doacao, excluir_doacao, config_pagina_doacao
from .recursos import recursos_hub, gerenciar_recurso, excluir_recurso, gerenciar_secao_recurso, excluir_secao_recurso
from .usuarios import gerenciar_usuarios, criar_usuario, editar_usuario, excluir_usuario, editar_pagina_membro
from .colunas import listar_colunas, criar_coluna, editar_coluna, excluir_coluna
from .relatorios_financeiros import relatorio_financeiro
from .financeiro import (
    financeiro_hub,
    gerenciar_plano_financeiro,
    gerenciar_adesao_financeira,
    gerenciar_cobranca_financeira,
    listar_auditoria_financeira,
    gerenciar_configuracao_gateway,
)
from .blogs import (
    blogs_hub, 
    gerenciar_post_blog, 
    excluir_post_blog, 
    configurar_rede_social_blog,
    gerenciar_membros_blog,
    excluir_membro_blog,
    # Categorias do blog:
    listar_categorias_blog,
    gerenciar_categoria_blog,
    excluir_categoria_blog
)