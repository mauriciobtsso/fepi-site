from django.contrib import admin
from .models import Livro, Categoria, LivrariaConfig

@admin.register(LivrariaConfig)
class LivrariaConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    fieldsets = (
        (None, {'fields': ('logo', 'instagram_widget_code')}),
    )

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'titulo', 'autor', 'categoria', 'destaque_home', 'preco', 'disponivel')
    list_filter = ('categoria', 'destaque_home', 'disponivel')
    list_editable = ('destaque_home', 'disponivel') # Adicionei disponivel para facilitar
    search_fields = ('titulo', 'autor', 'codigo')