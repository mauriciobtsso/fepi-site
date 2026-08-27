# painel/forms/__init__.py

from .noticias import NoticiaForm
from .site import PopupForm, YoutubeConfigForm, PostInstagramForm, PaginaInstitucionalForm, InformacaoContatoForm, ConfiguracaoEmailForm
from .intranet import CategoriaDocForm, DocumentoForm
from .programacao import AtividadeSemanalForm, DoutrinariaForm, CursoEventoForm
from .livraria import LivroForm, CategoriaLivroForm, LivrariaConfigForm
from .equipe import CargoForm, TipoDiretoriaForm, MembroDiretoriaForm
from .centros import CentroForm
from .doacoes import FormaDoacaoForm, PaginaDoacaoConfigForm
from .financeiro import (
    GatewayConfiguracaoForm,
    PlanoMensalidadeForm,
    AdesaoMensalidadeForm,
    CobrancaMensalidadeForm,
)
from .recursos import SecaoLinkForm, LinkItemForm
from .usuarios import PerfilForm
from .colunas import ColunaForm
from .blogs import PostBlogForm, ConfigBlogForm