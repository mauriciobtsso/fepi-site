from django.contrib import admin
from .models import Livro, Categoria, LivrariaConfig # <--- Novo Import

@admin.register(LivrariaConfig)
class LivrariaConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    # Ajuda o Django a gerir o upload da imagem de logo
    fieldsets = (
        (None, {'fields': ('logo', 'instagram_widget_code')}),
    )

# Atualiza Livro para mostrar o campo destaque
@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'titulo', 'autor', 'categoria', 'destaque_home', 'preco', 'disponivel') # Adicionado 'destaque_home'
    list_filter = ('categoria', 'destaque_home', 'disponivel')
    list_editable = ('destaque_home',) # Permite editar o destaque na lista
    search_fields = ('titulo', 'autor', 'codigo')