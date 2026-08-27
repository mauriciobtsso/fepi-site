# Webhooks financeiros da FEPI

## Objetivo

O aplicativo `financeiro` recebe notificações de mudança de status dos gateways e atualiza o banco interno somente depois de validar a autenticidade da requisição. O webhook não recebe login de usuário, não é uma tela do painel e não deve ser acionado manualmente em produção sem assinatura válida.

## Endpoints

| Gateway | Endpoint | Header principal |
|---|---|---|
| PagBank | `/webhooks/pagbank/` | `x-authenticity-token` |
| Pagar.me | `/webhooks/pagarme/` | `x-pagarme-signature` ou header equivalente configurado |

A URL completa deve ser informada no cadastro do webhook do provedor e também pode ser registrada em `GatewayConfiguracao.webhook_url`. O endpoint aceita somente `POST`, exige JSON, limita o corpo a 1 MiB e está protegido contra CSRF porque é chamado por serviço externo.

## Segredos

Os segredos não fazem parte do banco de dados, dos modelos ou do formulário administrativo. Eles devem ser configurados como variáveis protegidas no Railway/Render:

```text
PAGBANK_WEBHOOK_TOKEN=token-secreto-da-conta
PAGARME_WEBHOOK_SECRET=segredo-do-endpoint
```

No PagBank, a assinatura é calculada como SHA-256 de `token + '-' + corpo-bruto`. O valor recebido no header `x-authenticity-token` é comparado em tempo constante. O corpo bruto é usado, e não o JSON reformatado, para evitar divergência de hash [1].

Para o Pagar.me, o serviço aceita HMAC-SHA256 nos headers `x-pagarme-signature`, `x-signature`, `x-webhook-signature` ou `x-hub-signature-256`, em hexadecimal ou Base64. O header final usado pela conta deve ser confirmado durante a homologação do endpoint, pois a referência pública V5 descreve o envelope e os eventos, mas a configuração de assinatura pode variar conforme o canal/produto.

## Processamento

O fluxo é transacional. Primeiro, o serviço valida o gateway ativo em `GatewayConfiguracao`, lê o corpo bruto, interpreta o JSON e valida a assinatura. Depois, grava o evento em `EventoGateway` com o payload sanitizado, o tipo, o status e as tentativas. Campos potencialmente sensíveis, como cartão, número, CVV, tokens e segredos, são substituídos por `[REDACTED]` antes da persistência.

A idempotência usa a combinação `gateway + evento_id`, já protegida por constraint no banco. Uma repetição de um evento já processado retorna HTTP 200 com `already_processed` e não cria um segundo pagamento. Eventos com assinatura inválida são registrados como erro, mas não alteram cobrança ou adesão.

Quando há correspondência por ID de cobrança, fatura, referência, assinatura ou objeto do evento, o sistema pode atualizar a cobrança para `PAGO`, `ESTORNADA`, `CANCELADA`, `FALHA`, `PROCESSANDO` ou `PENDENTE`. Em uma confirmação de pagamento, cria ou atualiza `Pagamento`, registra data, valor, forma de pagamento e dados não sensíveis do gateway. Uma adesão pendente ou inadimplente volta a `ATIVA` somente quando uma cobrança é confirmada como paga.

O processador evita que um evento antigo regrida uma cobrança paga ou estornada. A auditoria técnica é registrada em `AuditoriaFinanceira` com `usuario=None`, pois a origem é o gateway, e contém o evento, o resultado e a mensagem de erro quando aplicável.

## Respostas

| Situação | Resposta |
|---|---:|
| Evento válido e processado | `200` |
| Evento já processado | `200` |
| Gateway não ativo | `503` |
| Assinatura ausente ou inválida | `401` |
| JSON inválido | `400` |
| Payload acima do limite | `413` |
| Erro de payload processável | `422` |
| Erro interno | `500`, para permitir nova tentativa do provedor |

O processamento não deve considerar o retorno do checkout como confirmação. A confirmação interna acontece pelo webhook autenticado ou por futura rotina de reconciliação que consulte o gateway.

## Homologação obrigatória

Antes de ativar a configuração em produção, devem ser cadastradas as variáveis no ambiente, configurado o endpoint HTTPS no sandbox, enviado um evento de teste de cada meio de pagamento e conferidos `EventoGateway`, `CobrancaMensalidade`, `Pagamento` e `AuditoriaFinanceira`. Também é necessário confirmar no ambiente do Pagar.me o header de assinatura efetivamente enviado e ajustar o adaptador, se a conta utilizar outro mecanismo.

### Referências

[1]: https://developer.pagbank.com.br/reference/confirmar-autenticidade-da-notificacao "PagBank — Confirm notification authenticity"
[2]: https://developer.pagbank.com.br/reference/webhooks-checkout "PagBank — Webhooks do Checkout"
[3]: https://docs.pagar.me/docs/webhooks "Pagar.me V5 — Webhooks"
[4]: https://docs.pagar.me/reference/vis%C3%A3o-geral-sobre-webhooks "Pagar.me V5 — Visão geral sobre Webhooks"
