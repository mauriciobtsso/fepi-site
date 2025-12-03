from django.contrib import admin
from .models import Centro

@admin.register(Centro)
class CentroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'tipo', 'telefone')
    list_filter = ('tipo', 'cidade')
    search_fields = ('nome', 'endereco')