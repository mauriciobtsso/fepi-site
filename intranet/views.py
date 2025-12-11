from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import DocumentoRestrito

@login_required  # <--- O "porteiro" que barra quem não tem senha
def area_federado(request):
    documentos = DocumentoRestrito.objects.all()
    
    # Agrupar documentos por categoria, se quiseres, ou mandar tudo junto
    # Aqui mandamos tudo e o template filtra ou mostra lista
    
    context = {
        'documentos': documentos,
        'user': request.user
    }
    return render(request, 'intranet/dashboard.html', context)