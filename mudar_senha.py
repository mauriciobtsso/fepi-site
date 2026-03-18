import os
import django

# Configurar o ambiente Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fepi_site.settings")
django.setup()

from django.contrib.auth import get_user_model

def forcar_nova_senha():
    User = get_user_model()
    USERNAME = "admin"
    NOVA_SENHA = "Admin@123"  # <--- A SENHA QUE VAI FICAR (Podes mudar aqui)

    try:
        user = User.objects.get(username=USERNAME)
        user.set_password(NOVA_SENHA)
        user.save()
        print(f"--- SUCESSO ABSOLUTO: Senha de '{USERNAME}' alterada! ---")
    except User.DoesNotExist:
        print(f"--- ERRO: O usuário '{USERNAME}' não existe no banco. ---")

if __name__ == "__main__":
    forcar_nova_senha()