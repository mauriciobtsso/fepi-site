from django.shortcuts import render
from .models import FormaDoacao

def doacoes_view(request):
    formas = FormaDoacao.objects.all()
    return render(request, 'doacoes/doacoes.html', {'formas': formas})