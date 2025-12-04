from django.contrib import admin
from .models import AtividadeSemanal, Doutrinaria, CursoEvento

@admin.register(AtividadeSemanal)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('dia', 'horario', 'nome')
    list_filter = ('dia',)

@admin.register(Doutrinaria)
class DoutrinariaAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'tema', 'palestrante')

@admin.register(CursoEvento)
class CursoEventoAdmin(admin.ModelAdmin):
    list_display = ('data_evento', 'titulo', 'local')
    search_fields = ('titulo',)