# blogs/admin.py
from django.contrib import admin
from .models import BlogDepartamento, PostBlog, BlogMembro

class BlogMembroInline(admin.TabularInline):
    model = BlogMembro
    extra = 1
    autocomplete_fields = ('usuario',)


@admin.register(BlogDepartamento)
class BlogDepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'subdominio', 'tema', 'ativo')
    list_filter = ('tema', 'ativo')
    search_fields = ('nome', 'subdominio')
    inlines = [BlogMembroInline]

@admin.register(BlogMembro)
class BlogMembroAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'blog', 'papel', 'ativo', 'criado_em')
    list_filter = ('blog', 'papel', 'ativo')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'blog__nome')


@admin.register(PostBlog)
class PostBlogAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'departamento', 'data_publicacao', 'publicado')
    list_filter = ('departamento', 'publicado')
    prepopulated_fields = {'slug': ('titulo',)} # Preenche o slug automaticamente