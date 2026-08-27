import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from financeiro.models import Gateway
from financeiro.services.webhooks import (
    MAX_WEBHOOK_BYTES,
    WebhookAuthenticationError,
    WebhookPayloadError,
    _validate_signature,
    configuracao_gateway_aceita,
    processar_webhook,
    registrar_webhook_erro,
    registrar_webhook_rejeitado,
)

logger = logging.getLogger(__name__)


_GATEWAYS_VALIDOS = {
    Gateway.PAGBANK: Gateway.PAGBANK,
    Gateway.PAGARME: Gateway.PAGARME,
}


@csrf_exempt
@require_POST
def gateway_webhook(request, gateway):
    """Recebe notificações autenticadas do provedor ativo e responde de forma idempotente."""
    provider = _GATEWAYS_VALIDOS.get((gateway or "").lower())
    if not provider:
        return JsonResponse({"detail": "Gateway não suportado."}, status=404)

    raw_body = request.body
    if len(raw_body) > MAX_WEBHOOK_BYTES:
        return JsonResponse({"detail": "Payload excede o limite permitido."}, status=413)

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"detail": "Payload JSON inválido."}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"detail": "O payload deve ser um objeto JSON."}, status=400)

    if not configuracao_gateway_aceita(provider):
        return JsonResponse({"detail": "Gateway não está ativo para recebimento."}, status=503)

    try:
        _validate_signature(provider, raw_body, request.headers)
    except WebhookAuthenticationError as exc:
        logger.warning("Webhook %s rejeitado: %s", provider, exc)
        registrar_webhook_rejeitado(provider, payload, raw_body, str(exc))
        return JsonResponse({"detail": "Webhook não autenticado."}, status=401)

    try:
        resultado = processar_webhook(provider, payload, raw_body)
    except WebhookPayloadError as exc:
        logger.warning("Webhook %s com payload inválido: %s", provider, exc)
        registrar_webhook_erro(provider, payload, raw_body, str(exc))
        return JsonResponse({"detail": "Payload não processado."}, status=422)
    except Exception:
        logger.exception("Erro inesperado ao processar webhook %s", provider)
        registrar_webhook_erro(provider, payload, raw_body, "Erro interno no processamento do webhook.")
        return JsonResponse({"detail": "Webhook recebido para reprocessamento."}, status=500)

    return JsonResponse({"received": True, **resultado}, status=200)
