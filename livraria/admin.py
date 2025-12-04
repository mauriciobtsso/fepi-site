from django.contrib import admin
from .models import Livro, Categoria

# Registra as Categorias para poderes criar/editar
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

# Atualiza o Livro para usar a nova categoria
@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'titulo', 'autor', 'categoria', 'preco', 'disponivel')
    list_filter = ('categoria', 'disponivel') # O filtro agora usa as categorias do banco
    search_fields = ('titulo', 'autor', 'codigo')