import json
from google import genai
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def chat_assistente_ia(request):
    """
    Endpoint para processar as requisições do chat da IA no painel usando o NOVO SDK do Google.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mensagem_usuario = data.get('mensagem', '')

            if not mensagem_usuario:
                return JsonResponse({'erro': 'Mensagem vazia'}, status=400)

            # Define a personalidade e as regras da IA da FEPI
            prompt_sistema = (
                "Você é o Assistente Virtual do painel administrativo da Federação Espírita Piauiense (FEPI). "
                "Sua função é auxiliar os voluntários e funcionários a criar notícias, revisar textos, "
                "sugerir títulos e explicar como usar o sistema. "
                "REGRA DE TOM E PERSONALIDADE: Seja extremamente prático, direto, moderno e profissional. "
                "NÃO seja 'meloso' e NÃO utilize jargões religiosos exagerados ou saudações doutrinárias longas "
                "(ex: evite 'Muita paz', 'Que a luz do mestre Jesus te envolva', 'Caro irmão', etc). "
                "Vá direto ao ponto para ajudar o usuário a ser produtivo. Seja cordial, mas focado no trabalho. "
                f"A mensagem do usuário é: {mensagem_usuario}"
            )

            # Verifica se a chave existe no settings.py
            chave_api = getattr(settings, 'GEMINI_API_KEY', None)
            if not chave_api:
                return JsonResponse({'erro': 'Chave da API não configurada no servidor.'}, status=500)

            # Inicializa o cliente com a NOVA biblioteca
            client = genai.Client(api_key=chave_api)

            # Faz a chamada usando a nova estrutura e o modelo atualizado e gratuito
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt_sistema
            )

            return JsonResponse({'resposta': response.text})

        except Exception as e:
            return JsonResponse({'erro': f'Erro na API: {str(e)}'}, status=500)
            
    return JsonResponse({'erro': 'Método não permitido'}, status=405)