from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns('',
    # 1. Rota para o site principal (www ou raiz vazia)
    host(r'(www)?', 'fepi_site.urls', name='www'),
    
    # 2. Rota para os departamentos (subdomínios dinâmicos)
    host(r'(?P<subdominio>[a-zA-Z0-9-]+)', 'blogs.urls_subdominio', name='departamento'),
    
    # 3. Fallback de segurança global para o site principal
    host(r'.*', 'fepi_site.urls', name='default'),
)