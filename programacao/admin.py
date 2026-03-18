from django.contrib import admin
from .models import AtividadeSemanal, Doutrinaria, CursoEvento

admin.site.register(AtividadeSemanal)
admin.site.register(Doutrinaria)

@admin.register(CursoEvento)
class CursoEventoAdmin(admin.ModelAdmin):
    list_display = ('data_evento', 'titulo', 'local')
    prepopulated_fields = {'slug': ('titulo',)} # <--- Magia aqui