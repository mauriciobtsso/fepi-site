from django.contrib import admin
from .models import Livro

# Isto cria uma tabela bonita no admin
@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'preco', 'disponivel')
    search_fields = ('titulo', 'autor')