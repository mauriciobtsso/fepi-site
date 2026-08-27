# Modelo financeiro inicial da FEPI

## Objetivo

O aplicativo `financeiro` foi criado para separar mensalidades associativas de doações espontâneas. Nesta primeira etapa, ele contém somente o domínio de dados e o registro administrativo; não cria cobranças reais, não chama gateways e não armazena dados de cartão.

## Entidades e relacionamento

| Entidade | Papel no domínio | Relações principais |
|---|---|---|
| `PlanoMensalidade` | Define nome, valor, dia de vencimento e gateway associado. | Um plano possui várias adesões. |
| `AdesaoMensalidade` | Representa o vínculo de um usuário a um plano, preservando o valor e o vencimento contratados. | Pertence a um federado e a um plano; possui várias cobranças. |
| `CobrancaMensalidade` | Representa uma competência individual, com vencimento, valor, boleto, Pix, URL e status. | Pertence a uma adesão; possui tentativas de pagamento e eventos. |
| `Pagamento` | Registra uma tentativa ou confirmação de pagamento de uma cobrança. | Pertence a uma cobrança. |
| `EventoGateway` | Guarda o webhook recebido, sua validação, processamento, erro e vínculo interno. | Pode apontar para uma adesão e/ou cobrança. |
| `AuditoriaFinanceira` | Registra ações administrativas e snapshots antes/depois. | Usa `ContentType` para auditar qualquer objeto financeiro. |

## Decisões de integridade

Os valores monetários usam `DecimalField` com duas casas decimais e validação para impedir valores negativos. O dia de vencimento é limitado de 1 a 28 para evitar ambiguidades em meses com quantidade diferente de dias. Uma adesão não pode ter data final anterior ao início.

A combinação de adesão e competência é única, impedindo duas cobranças para o mesmo federado no mesmo mês. IDs externos de plano, assinatura, fatura e cobrança possuem unicidade condicional quando preenchidos. O evento externo é único por gateway e `evento_id`, permitindo receber o mesmo identificador em gateways diferentes e, ao mesmo tempo, impedir processamento duplicado no mesmo gateway.

Os relacionamentos financeiros usam `PROTECT` quando a remoção apagaria histórico. Eventos e auditorias não podem ser apagados pelo Django Admin. Credenciais, tokens de cartão, CVV e números de cartão não fazem parte do modelo.

## Status internos

Os status internos não dependem dos nomes específicos do gateway. Isso permite trocar PagBank por Pagar.me sem alterar a experiência do federado.

| Objeto | Estados principais |
|---|---|
| Adesão | Pendente de ativação, ativa, suspensa, inadimplente, cancelada e encerrada. |
| Cobrança | Aguardando pagamento, processando, pago, vencida, falha, cancelada, estornada e conciliação manual. |
| Pagamento | Pendente, em análise, autorizado, pago, falhou, cancelado e estornado. |
| Evento | Recebido, processado, erro no processamento e ignorado. |

## Arquivos implementados

`financeiro/models.py` contém o domínio, `financeiro/admin.py` registra filtros e pesquisas no painel, `financeiro/migrations/0001_initial.py` cria o schema inicial e `financeiro/migrations/0002_cobrancamensalidade_documento_pagador_and_more.py` adiciona os snapshots de pagador e a expiração do Pix. O app foi adicionado a `INSTALLED_APPS` em `fepi_site/settings.py`.

Os testes em `financeiro/tests.py` cobrem a unicidade por competência, a propriedade de vencimento, a idempotência de eventos e a possibilidade de IDs iguais em gateways distintos.

## Próximas extensões

A próxima camada deverá criar serviços de gateway atrás de uma interface comum, por exemplo `criar_cliente`, `criar_assinatura`, `gerar_cobranca`, `cancelar_adesao` e `consultar_status`. Os webhooks deverão validar autenticidade, registrar o payload em `EventoGateway`, usar idempotência e atualizar o status interno somente após confirmação válida. A Área do Federado e o painel deverão consultar o banco interno, não o gateway diretamente.

O PagBank documenta recorrência via API com boleto ou cartão, webhooks para mudanças de status e validação de autenticidade por SHA256 [1] [2]. O Pagar.me documenta eventos de assinaturas, faturas e cobranças, além de reenvio de webhooks [3]. A implementação futura deverá ser baseada na documentação vigente do gateway escolhido e em ambiente sandbox antes de qualquer ativação em produção.

### Referências

[1]: https://faq.pagbank.com.br/duvida/como-criar-um-plano-de-pagamento-recorrente/119 "FAQ PagBank — Como criar um plano de pagamento recorrente"
[2]: https://developer.pagbank.com.br/reference/webhooks-checkout "PagBank — Webhooks do Checkout"
[3]: https://docs.pagar.me/docs/webhooks "Pagar.me V5 — Webhooks"
