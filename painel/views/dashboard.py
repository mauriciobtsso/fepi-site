# painel/views/dashboard.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from noticias.models import Noticia
from .auth import check_acesso_painel

@login_required(login_url='/login/')
@user_passes_test(check_acesso_painel, login_url='/usuarios/minha-conta/')
def dashboard(request):
    ultimas_noticias = Noticia.objects.all().order_by('-data_publicacao')[:5]
    return render(request, 'painel/dashboard.html', {'ultimas_noticias': ultimas_noticias})