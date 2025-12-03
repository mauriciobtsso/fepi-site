from django.contrib import admin
from django.urls import path
from core.views import home  # Importamos a função home que criamos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # O '' vazio significa "página inicial"
]