from django.conf import settings


class SubdomainBlogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower().rstrip('.')
        base_domain = getattr(settings, 'PARENT_HOST', 'fepiaui.org.br').split(':')[0].lower()
        is_official_subdomain = (
            host.endswith(f'.{base_domain}')
            and host.count('.') == base_domain.count('.') + 1
        )
        rotas_ignoradas = ('/admin/', '/painel/', '/media/', '/static/')

        # Só reescreve subdomínios oficiais de um nível, como dapse.fepiaui.org.br.
        # Hosts do Render, Railway, localhost e domínios desconhecidos seguem o fluxo normal.
        if is_official_subdomain and not request.path_info.startswith(rotas_ignoradas):
            subdominio = host[:-(len(base_domain) + 1)]
            if not request.path_info.startswith('/blogs/'):
                request.path_info = f'/blogs/{subdominio}{request.path_info}'

        return self.get_response(request)
