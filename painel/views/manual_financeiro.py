from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from .auth import is_admin


PAINEL_LOGIN = "/usuarios/minha-conta/"


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url=PAINEL_LOGIN)
def manual_financeiro(request):
    return render(request, "painel/financeiro/manual.html")
