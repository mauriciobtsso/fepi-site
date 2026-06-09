# painel/views/auth.py
from django.contrib.auth.models import User

def check_acesso_painel(user):
    if user.is_superuser:
        return True
    if hasattr(user, 'perfil') and user.perfil.is_colunista and user.perfil.status == 'APROVADO':
        return True
    return False

def is_admin(user):
    return user.is_superuser