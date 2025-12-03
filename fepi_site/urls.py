from django.contrib import admin
from django.urls import path
from core.views import home

# Imports para as imagens funcionarem
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
]

# Adiciona a rota de imagens apenas se estivermos em modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)