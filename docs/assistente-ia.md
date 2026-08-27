# Assistente de IA da FEPI

## Objetivo

O assistente do painel atende administradores e colaboradores da FEPI em Português do Brasil. Ele orienta o uso do painel, ajuda na redação de notícias, eventos e colunas e consulta o manual interno do módulo financeiro quando a pergunta envolve mensalidades, adesões, cobranças, gateway, doações, inadimplência ou webhooks.

## Arquitetura atual

A rota autenticada é `POST /painel/api/assistente-ia/`. O endpoint mantém um prompt institucional comum e acrescenta o conteúdo de `painel/templates/painel/financeiro/manual_conteudo.html` apenas quando a mensagem contém termos financeiros. O manual é carregado uma vez por processo e mantido em cache, evitando leitura do disco em todas as perguntas.

O Gemini é o primeiro provedor, usando `gemini-3-flash-preview`, que é o identificador válido documentado para a família Gemini 3 Flash. O Groq é o fallback, usando por padrão `openai/gpt-oss-20b`, identificador de produção documentado pela Groq. O fallback não expõe a mensagem técnica original para o usuário e registra apenas o tipo da exceção e o provedor que falhou.

## Configurações de ambiente

```text
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-3-flash-preview
GEMINI_TIMEOUT_MS=30000
GEMINI_MAX_RETRIES=2

GROQ_API_KEY=...
GROQ_MODEL=openai/gpt-oss-20b
GROQ_TIMEOUT_SECONDS=25
GROQ_MAX_RETRIES=1

AI_MAX_MESSAGE_CHARS=4000
```

As chaves devem ser configuradas nas variáveis protegidas do Railway ou Render. Elas não devem ser inseridas no painel, commitadas no GitHub ou incluídas no manual.

## Melhorias de estabilidade

O cliente Google agora usa timeout em milissegundos, com duas tentativas e atraso controlado. A configuração anterior usava `45.0`; no SDK instalado, a propriedade é definida em milissegundos, portanto esse valor era incompatível com a intenção de aguardar 45 segundos. O padrão novo de 30.000 ms evita tanto o abandono prematuro quanto processos indefinidamente pendurados.

O cliente Groq usa timeout explícito de 25 segundos e uma retentativa. O backend valida método, JSON, tipo da mensagem, mensagem vazia e tamanho máximo. Erros de provedor são registrados no log sem incluir o texto do usuário ou chaves. Quando os dois provedores falham, a API retorna uma mensagem controlada com HTTP 503.

No navegador, uma segunda pergunta não é enviada enquanto a primeira está em processamento. A requisição possui `AbortController` de 45 segundos, o botão é desabilitado durante a chamada e respostas Markdown passam por sanitização com DOMPurify. A mensagem do usuário e mensagens de erro são inseridas via `textContent`, evitando interpretar entrada como HTML.

## Manual financeiro

O manual está em `/painel/financeiro/manual/` e é acessível a administradores autorizados. A página orienta sobre:

- primeiros passos do módulo;
- cadastro de usuários, federados, associados e formas de doação;
- distinção entre doador e federado;
- criação de planos;
- associação de qualquer usuário, inclusive inativo ou sem acesso à Área do Federado;
- registro de competências e cobranças;
- configuração de PagBank ou Pagar.me;
- webhooks e confirmação de pagamento;
- relatório de fluxo e inadimplência;
- auditoria, segurança e solução de problemas.

A mesma fonte de conteúdo é usada na página e no prompt financeiro do assistente, reduzindo o risco de a interface ensinar um procedimento diferente do que a IA responde.

## Regras de resposta financeira

O assistente deve dizer claramente quando uma função é futura ou quando não pode consultar dados individuais. Ele não deve inventar saldo, pagamento, vencimento, plano, status de cobrança, link de boleto ou permissão. Também não deve solicitar ou repetir token, senha, CVV, número de cartão ou segredo de webhook.

A confirmação de pagamento continua dependendo do webhook ou de uma conciliação administrativa. O assistente não deve marcar uma cobrança como paga nem orientar baixa manual sem comprovação.

## Checklist de produção

1. Configurar `GEMINI_API_KEY` e `GROQ_API_KEY` como segredos no provedor de hospedagem.
2. Confirmar que `GEMINI_MODEL` e `GROQ_MODEL` continuam disponíveis nos respectivos catálogos oficiais.
3. Testar uma pergunta editorial e uma pergunta financeira em produção controlada.
4. Testar o fallback desligando temporariamente o provedor primário em ambiente de homologação.
5. Verificar logs sem registrar mensagens privadas ou segredos.
6. Confirmar que o manual da página e o manual carregado pela IA estão no mesmo commit.
7. Revisar periodicamente o manual após cada mudança de rota, permissão ou fluxo financeiro.

## Referências técnicas

- Google AI for Developers — [Gemini 3 Flash preview](https://ai.google.dev/gemini-api/docs/models/gemini-3-flash-preview)
- GroqDocs — [OpenAI GPT OSS 20B](https://console.groq.com/docs/model/openai/gpt-oss-20b)
- GroqDocs — [Supported Models](https://console.groq.com/docs/models)
