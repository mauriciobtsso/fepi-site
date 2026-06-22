# blogs/middleware.py

class SubdomainBlogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pega o host da requisição (ex: dije.fepiaui.org.br ou localhost:8000)
        host = request.get_host().split(':')[0] 
        
        # Lista de domínios principais onde o interceptador NÃO deve atuar
        dominios_ignorados = ['127.0.0.1', 'localhost', 'fepiaui.org.br', 'www.fepiaui.org.br', 'seu-app.railway.app']
        
        # Rotas de sistema que não devem sofrer alteração
        rotas_ignoradas = ('/admin/', '/painel/', '/media/', '/static/')
        
        if host not in dominios_ignorados and not request.path_info.startswith(rotas_ignoradas):
            # Extrai o subdomínio (ex: 'dije' de 'dije.fepiaui.org.br')
            subdominio = host.split('.')[0]
            
            # Evita loop infinito caso a URL interna já tenha sido processada
            if not request.path_info.startswith('/blogs/'):
                # Reescreve o caminho internamente para o Django processar
                # Exemplo: O usuário acessa "/" no subdomínio, o Django lê como "/blogs/dije/"
                request.path_info = f'/blogs/{subdominio}{request.path_info}'

        response = self.get_response(request)
        return response