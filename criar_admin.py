import os
import django

# 1. Configurar o ambiente Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fepi_site.settings")
django.setup()

from django.contrib.auth import get_user_model

# 2. Definir os dados do Administrador
User = get_user_model()
USERNAME = "admin"
EMAIL = "admin@fepi.org.br"
PASSWORD = "admin"  # <--- TROCA ISTO POR UMA SENHA SEGURA!

# 3. Criar o usuário se ele não existir
def criar_superusuario():
    if not User.objects.filter(username=USERNAME).exists():
        print(f"--- CRIANDO SUPERUSER: {USERNAME} ---")
        User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
        print("--- SUCESSO: Superusuário criado! ---")
    else:
        print("--- AVISO: O Superusuário já existe. Ignorando. ---")

if __name__ == "__main__":
    criar_superusuario()