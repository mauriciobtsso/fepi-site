from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns('',
    # 1. Força subdomínios "www" a caírem no site principal
    host(r'www\..*', 'fepi_site.urls', name='www'),
    
    # 2. Ignora os domínios raiz para não dar conflito
    host(r'(fepiaui\.org\.br|localhost|127\.0\.0\.1|fepi\.cewantuildefreitas\.com\.br|fepiaui\.cewantuildefreitas\.com\.br)', 'fepi_site.urls', name='base'),
    
    # 3. A MÁGICA: Captura qualquer subdomínio dinâmico e envia para o blog.
    # Ex: Em "dije.localhost", ele guarda "dije" na variável 'subdominio' e passa para as views!
    host(r'(?P<subdominio>[a-zA-Z0-9-]+)\.(fepiaui\.org\.br|localhost|cewantuildefreitas\.com\.br|up\.railway\.app)', 'blogs.urls_subdominio', name='departamento'),
    
    # 4. Fallback de segurança para o site principal
    host(r'.*', 'fepi_site.urls', name='default'),
)