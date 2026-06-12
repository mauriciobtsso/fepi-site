import json
from google import genai as google_genai
from groq import Groq
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def chat_assistente_ia(request):
    """
    Endpoint com sistema de fallback automático: tenta Gemini primeiro pelo tom,
    se falhar aciona o Groq (Llama 3.1) como plano B estável.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mensagem_usuario = data.get('mensagem', '')

            if not mensagem_usuario:
                return JsonResponse({'erro': 'Mensagem vazia'}, status=400)

            # ------------------------------------------------------------
            # TENTATIVA 1: GOOGLE GEMINI (Tom ideal do painel)
            # ------------------------------------------------------------
            chave_gemini = getattr(settings, 'GEMINI_API_KEY', None)
            if chave_gemini:
                try:
                    client_google = google_genai.Client(api_key=chave_gemini)
                    
                    prompt_sistema_gemini = (
                        "Você é o Assistente Virtual do painel administrativo da Federação Espírita Piauiense (FEPI). "
                        "Sua função é auxiliar os voluntários e funcionários a criar notícias, revisar textos, "
                        "sugerir títulos e explicar como usar o sistema. "
                        "REGRA DE TOM E PERSONALIDADE: Seja extremamente prático, direto, moderno e profissional. "
                        "NÃO seja 'meloso' e NÃO utilize jargões religiosos exagerados ou saudações doutrinárias longas. "
                        "Vá direto ao ponto para ajudar o usuário a ser produtivo. Seja cordial, mas focado no trabalho."
                    )

                    response = client_google.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=f"{prompt_sistema_gemini}\n\nUsuário: {mensagem_usuario}"
                    )
                    
                    # Se chegou aqui, deu certo! Retorna a resposta do Gemini
                    return JsonResponse({'resposta': response.text})
                    
                except Exception as e_google:
                    # Se falhar (erro 503, por exemplo), não trava. Apenas avisa o log e passa para o plano B
                    print(f"[IA FEPI] Gemini instável ({str(e_google)}). Acionando plano B (Groq)...")
                    pass

            # ------------------------------------------------------------
            # TENTATIVA 2 (FALLBACK): GROQ LLAMA 3.1 (Estabilidade máxima)
            # ------------------------------------------------------------
            chave_groq = getattr(settings, 'GROQ_API_KEY', None)
            if not chave_groq:
                return JsonResponse({'erro': 'O serviço de inteligência artificial está temporariamente indisponível.'}, status=500)

            client_groq = Groq(api_key=chave_groq)
            modelo_groq = getattr(settings, 'GROQ_MODEL', 'llama-3.1-8b-instant')

            prompt_sistema_groq = (
                "Você é o Assistente de Inteligência Artificial do painel da Federação Espírita Piauiense (FEPI). "
                "Sua função é ajudar os voluntários a redigir notícias de forma ágil. "
                "DIRETRIZES OBRIGATÓRIAS: "
                "1. Responda em Português do Brasil natural, fluente e simpático. "
                "2. Seja direto e profissional, sem jargões religiosos. "
                "3. Use SEMPRE o termo correto 'Rodas de Conversa'. NUNCA use a palavra 'rondas'."
            )

            chat_completion = client_groq.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt_sistema_groq},
                    {"role": "user", "content": mensagem_usuario}
                ],
                model=modelo_groq,
            )
            
            resposta_groq = chat_completion.choices[0].message.content
            return JsonResponse({'resposta': resposta_groq})

        except Exception as e:
            return JsonResponse({'erro': f'Ocorreu um erro geral de comunicação com o assistente: {str(e)}'}, status=500)
            
    return JsonResponse({'erro': 'Método não permitido'}, status=405)