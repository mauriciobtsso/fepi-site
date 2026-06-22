# blogs/admin.py
from django.contrib import admin
from .models import BlogDepartamento, PostBlog

@admin.register(BlogDepartamento)
class BlogDepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'subdominio', 'ativo')
    search_fields = ('nome', 'subdominio')

@admin.register(PostBlog)
class PostBlogAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'departamento', 'data_publicacao', 'publicado')
    list_filter = ('departamento', 'publicado')
    prepopulated_fields = {'slug': ('titulo',)} # Preenche o slug automaticamente