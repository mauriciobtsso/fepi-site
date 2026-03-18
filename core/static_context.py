"""Context processor para servir URLs de arquivos estáticos via Cloudinary"""
import os
from urllib.parse import urljoin

def static_urls(request):
    """
    Context processor que fornece URLs de arquivos estáticos.
    Em produção (Railway), usa Cloudinary.
    Em desenvolvimento local, usa /static/
    """
    # Cloudinary config
    cloudinary_cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dym1yoj68')
    
    # Base URL para Cloudinary
    cloudinary_base = f"https://res.cloudinary.com/{cloudinary_cloud_name}/image/upload"
    
    # Determina se estamos em produção
    is_production = 'DATABASE_URL' in os.environ
    
    # URLs das imagens
    static_urls_dict = {
        'logo_webp': f"{cloudinary_base}/static/img/logo.webp" if is_production else "/static/img/logo.webp",
        'logo_png': f"{cloudinary_base}/static/img/logo.png" if is_production else "/static/img/logo.png",
        'favicon': f"{cloudinary_base}/static/img/favicon.png" if is_production else "/static/img/favicon.png",
    }
    
    return {'static_urls': static_urls_dict}
