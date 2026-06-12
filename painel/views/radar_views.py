import feedparser
import urllib.parse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def radar_noticias(request):
    """
    Busca notícias sobre o universo espírita usando o RSS do Google News.
    Permite filtros dinâmicos de termos e período.
    """
    # 1. Definimos os padrões iniciais
    termos_padrao = "Espiritismo OR Kardecista OR Kardecismo"
    periodo_padrao = "2d" # 2 dias
    
    # 2. Pegamos o que o usuário digitou no formulário (se houver)
    termos = request.GET.get('termos', termos_padrao)
    periodo = request.GET.get('periodo', periodo_padrao)
    
    # 3. Preparamos os termos para a URL (substitui espaços por +, etc)
    query_formatada = urllib.parse.quote_plus(termos)
    
    # 4. Montamos a URL do Google News dinamicamente
    url_rss = f"https://news.google.com/rss/search?q={query_formatada}+when:{periodo}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    
    feed = feedparser.parse(url_rss)
    noticias = []
    
    # Pegamos até 20 notícias
    for entry in feed.entries[:20]:
        noticias.append({
            'titulo': entry.title,
            'link': entry.link,
            'data': entry.published[0:16] if hasattr(entry, 'published') else '',
            'fonte': entry.source.title if hasattr(entry, 'source') else 'Internet'
        })
        
    # 5. Enviamos as notícias e os filtros atuais de volta para a tela
    context = {
        'noticias_radar': noticias,
        'termos_atuais': termos,
        'periodo_atual': periodo
    }
    
    return render(request, 'painel/radar_noticias.html', context)