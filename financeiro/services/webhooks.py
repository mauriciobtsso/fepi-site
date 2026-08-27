import base64
import hashlib
import hmac
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from financeiro.models import (
    AcaoAuditoria,
    AdesaoMensalidade,
    AuditoriaFinanceira,
    CobrancaMensalidade,
    EventoGateway,
    FormaPagamento,
    Gateway,
    GatewayConfiguracao,
    Pagamento,
    StatusAdesao,
    StatusCobranca,
    StatusEvento,
    StatusPagamento,
)


MAX_WEBHOOK_BYTES = 1024 * 1024
SUPPORTED_GATEWAYS = {Gateway.PAGBANK, Gateway.PAGARME}
SENSITIVE_KEYS = {
    "authorization",
    "access_token",
    "api_key",
    "card",
    "card_number",
    "cvv",
    "security_code",
    "number",
    "token",
}


class WebhookError(Exception):
    """Erro controlado de validação ou normalização de um webhook."""


class WebhookAuthenticationError(WebhookError):
    pass


class WebhookPayloadError(WebhookError):
    pass


def _secret(name):
    return os.environ.get(name) or getattr(settings, name, "")


def _sanitizar(value, key=""):
    """Remove campos potencialmente sensíveis antes de persistir o payload."""
    if key.lower() in SENSITIVE_KEYS or any(part in key.lower() for part in ("token", "secret", "password", "cvv")):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(k): _sanitizar(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitizar(item) for item in value]
    return value


def _first_value(*values):
    for value in values:
        if value not in (None, ""):
            return value
    return None


def _nested(payload, *paths):
    values = []
    for path in paths:
        current = payload
        for part in path:
            if not isinstance(current, dict):
                current = None
                break
            current = current.get(part)
        values.append(current)
    return _first_value(*values)


def _candidate_ids(payload):
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    charge = payload.get("charge") if isinstance(payload.get("charge"), dict) else {}
    invoice = data.get("invoice") if isinstance(data.get("invoice"), dict) else {}
    subscription = data.get("subscription") if isinstance(data.get("subscription"), dict) else {}
    values = [
        payload.get("id"),
        payload.get("code"),
        payload.get("reference_id"),
        payload.get("reference"),
        payload.get("charge_id"),
        payload.get("invoice_id"),
        payload.get("subscription_id"),
        data.get("id"),
        data.get("reference_id"),
        data.get("charge_id"),
        data.get("invoice_id"),
        data.get("subscription_id"),
        charge.get("id"),
        invoice.get("id"),
        subscription.get("id"),
        _nested(payload, ("data", "charge", "id"), ("data", "invoice", "id"), ("data", "subscription", "id")),
    ]
    return {str(value) for value in values if value not in (None, "")}


def _event_id(payload, raw_body):
    event_id = _first_value(
        payload.get("event_id"),
        payload.get("id"),
        payload.get("notification_id"),
        _nested(payload, ("data", "id"), ("data", "event_id")),
    )
    return str(event_id) if event_id else f"body-sha256:{hashlib.sha256(raw_body).hexdigest()}"


def _event_type(payload, provider):
    event = _first_value(payload.get("event"), payload.get("type"), payload.get("event_type"))
    if event:
        return str(event).lower()
    status = _first_value(payload.get("status"), _nested(payload, ("data", "status"), ("charge", "status")))
    return f"{provider}.payment.{str(status).lower()}" if status else f"{provider}.payment.unknown"


def _status_token(payload):
    event = _event_type(payload, "")
    status = _first_value(
        payload.get("status"),
        payload.get("payment_status"),
        _nested(payload, ("data", "status"), ("data", "payment_status"), ("charge", "status"), ("invoice", "status")),
    )
    return f"{event} {status or ''}".lower().replace("-", "_")


def _status_cobranca(payload):
    token = _status_token(payload)
    if any(value in token for value in ("paid", "pago", "captured")):
        return StatusCobranca.PAGO
    if any(value in token for value in ("refunded", "estornado", "chargeback")):
        return StatusCobranca.ESTORNADA
    if any(value in token for value in ("canceled", "cancelled", "cancelado")):
        return StatusCobranca.CANCELADA
    if any(value in token for value in ("failed", "failure", "declined", "falha", "denied")):
        return StatusCobranca.FALHA
    if any(value in token for value in ("pending", "waiting", "pendente", "processing", "in_analysis")):
        return StatusCobranca.PROCESSANDO if "processing" in token or "in_analysis" in token else StatusCobranca.PENDENTE
    return None


def _status_adesao(payload):
    token = _status_token(payload)
    if "cancel" in token:
        return StatusAdesao.CANCELADA
    if "suspend" in token:
        return StatusAdesao.SUSPENSA
    if any(value in token for value in ("activated", "active", "created", "paid")):
        return StatusAdesao.ATIVA
    return None


def _deve_atualizar_cobranca(atual, novo):
    if atual == StatusCobranca.ESTORNADA:
        return False
    if atual == StatusCobranca.PAGO and novo not in {StatusCobranca.ESTORNADA, StatusCobranca.CANCELADA}:
        return False
    return True


def _status_pagamento(status_cobranca):
    return {
        StatusCobranca.PAGO: StatusPagamento.PAGO,
        StatusCobranca.ESTORNADA: StatusPagamento.ESTORNADO,
        StatusCobranca.CANCELADA: StatusPagamento.CANCELADO,
        StatusCobranca.FALHA: StatusPagamento.FALHOU,
        StatusCobranca.PROCESSANDO: StatusPagamento.EM_ANALISE,
        StatusCobranca.PENDENTE: StatusPagamento.PENDENTE,
    }.get(status_cobranca)


def _decimal(value):
    if value in (None, ""):
        return None
    try:
        decimal = Decimal(str(value))
        # PagBank and Pagar.me may send cents in integer amount fields.
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit() and "." not in value):
            decimal = decimal / Decimal("100")
        return decimal
    except (InvalidOperation, TypeError, ValueError):
        return None


def _amount(payload):
    value = _first_value(
        payload.get("amount"),
        payload.get("value"),
        _nested(payload, ("data", "amount"), ("data", "value"), ("charge", "amount"), ("charge", "amount", "value")),
    )
    if isinstance(value, dict):
        value = _first_value(value.get("value"), value.get("amount"), value.get("total"))
    return _decimal(value)


def _parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value if timezone.is_aware(value) else timezone.make_aware(value)
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if timezone.is_aware(parsed) else timezone.make_aware(parsed)


def _payment_method(payload):
    method = _first_value(
        payload.get("payment_method"),
        payload.get("method"),
        _nested(payload, ("data", "payment_method"), ("data", "method"), ("charge", "payment_method")),
    )
    if isinstance(method, dict):
        method = _first_value(method.get("type"), method.get("method"), method.get("name"))
    token = str(method or "").lower()
    if "pix" in token:
        return FormaPagamento.PIX
    if "boleto" in token or "bank_slip" in token:
        return FormaPagamento.BOLETO
    return FormaPagamento.CARTAO


def _gateway_charge_id(payload):
    return _first_value(
        payload.get("charge_id"),
        _nested(payload, ("data", "charge_id"), ("charge", "id"), ("data", "charge", "id")),
    )


def _gateway_invoice_id(payload):
    return _first_value(
        payload.get("invoice_id"),
        _nested(payload, ("data", "invoice_id"), ("invoice", "id"), ("data", "invoice", "id")),
    )


def _gateway_payment_id(payload):
    return _first_value(
        payload.get("payment_id"),
        payload.get("transaction_id"),
        _nested(payload, ("data", "payment_id"), ("data", "transaction_id"), ("charge", "payment_id"), ("charge", "transaction_id")),
    )


def _find_records(provider, payload):
    ids = _candidate_ids(payload)
    if not ids:
        return None, None
    cobranca = CobrancaMensalidade.objects.select_related("adesao", "adesao__federado").filter(
        Q(gateway=provider)
        & (
            Q(gateway_charge_id__in=ids)
            | Q(gateway_invoice_id__in=ids)
            | Q(adesao__gateway_subscription_id__in=ids)
            | Q(adesao__gateway_reference__in=ids)
        )
    ).first()
    adesao = cobranca.adesao if cobranca else AdesaoMensalidade.objects.filter(
        gateway=provider,
    ).filter(
        Q(gateway_subscription_id__in=ids) | Q(gateway_reference__in=ids)
    ).first()
    return cobranca, adesao


def _validate_signature(provider, raw_body, headers):
    if provider == Gateway.PAGBANK:
        token = _secret("PAGBANK_WEBHOOK_TOKEN")
        received = headers.get("x-authenticity-token", "")
        if not token or not received:
            raise WebhookAuthenticationError("Token ou assinatura do PagBank não configurado.")
        expected = hashlib.sha256(token.encode() + b"-" + raw_body).hexdigest()
        if not hmac.compare_digest(expected, received.strip()):
            raise WebhookAuthenticationError("Assinatura do PagBank inválida.")
        return True

    if provider == Gateway.PAGARME:
        secret = _secret("PAGARME_WEBHOOK_SECRET")
        received = _first_value(
            headers.get("x-pagarme-signature"),
            headers.get("x-signature"),
            headers.get("x-webhook-signature"),
            headers.get("x-hub-signature-256"),
        )
        if not secret or not received:
            raise WebhookAuthenticationError("Segredo ou assinatura do Pagar.me não configurado.")
        received = str(received).strip()
        if received.startswith("sha256="):
            received = received.split("=", 1)[1]
        digest = hmac.new(secret.encode(), raw_body, hashlib.sha256)
        valid = hmac.compare_digest(digest.hexdigest(), received) or hmac.compare_digest(
            base64.b64encode(digest.digest()).decode(), received
        )
        if not valid:
            raise WebhookAuthenticationError("Assinatura do Pagar.me inválida.")
        return True

    raise WebhookAuthenticationError("Gateway não suportado.")


def _make_audit(evento, descricao, dados_novos=None):
    return AuditoriaFinanceira.objects.create(
        usuario=None,
        acao=AcaoAuditoria.CONCILIACAO,
        content_type=ContentType.objects.get_for_model(evento),
        object_id=evento.pk,
        descricao=descricao,
        dados_anteriores={},
        dados_novos=dados_novos or {"evento_id": evento.evento_id, "status": evento.status},
    )


def _register_event(provider, payload, raw_body, signature_valid, error=""):
    event_id = _event_id(payload, raw_body)
    event, created = EventoGateway.objects.get_or_create(
        gateway=provider,
        evento_id=event_id,
        defaults={
            "tipo_evento": _event_type(payload, provider),
            "status": StatusEvento.RECEBIDO if signature_valid else StatusEvento.ERRO,
            "assinatura_validada": signature_valid,
            "payload": _sanitizar(payload),
            "erro_processamento": error,
        },
    )
    if not created and signature_valid and event.status == StatusEvento.PROCESSADO:
        return event, False
    if not created:
        event.tipo_evento = _event_type(payload, provider)
        event.payload = _sanitizar(payload)
        event.assinatura_validada = signature_valid
        event.status = StatusEvento.RECEBIDO if signature_valid else StatusEvento.ERRO
        event.erro_processamento = error
        event.save(update_fields=["tipo_evento", "payload", "assinatura_validada", "status", "erro_processamento"])
    return event, True


def processar_webhook(provider, payload, raw_body):
    """Valida, registra e processa um evento já autenticado."""
    with transaction.atomic():
        evento, should_process = _register_event(provider, payload, raw_body, True)
        if not should_process:
            return {"event_id": evento.evento_id, "status": "already_processed"}

        cobranca, adesao = _find_records(provider, payload)
        evento.adesao = adesao
        evento.cobranca = cobranca
        evento.tentativas = (evento.tentativas or 0) + 1

        status_cobranca = _status_cobranca(payload)
        status_adesao = _status_adesao(payload)
        if adesao and status_adesao and _event_type(payload, provider).startswith(("subscription", "assinatura")):
            adesao.status = status_adesao
            adesao.save(update_fields=["status", "atualizado_em"])

        if cobranca and status_cobranca and not _deve_atualizar_cobranca(cobranca.status, status_cobranca):
            status_cobranca = None

        if cobranca and status_cobranca:
            agora = timezone.now()
            cobranca.status = status_cobranca
            cobranca.ultima_sincronizacao = agora
            cobranca.dados_gateway = _sanitizar(payload)
            external_charge_id = _gateway_charge_id(payload)
            external_invoice_id = _gateway_invoice_id(payload)
            if external_charge_id and not cobranca.gateway_charge_id:
                cobranca.gateway_charge_id = str(external_charge_id)
            if external_invoice_id and not cobranca.gateway_invoice_id:
                cobranca.gateway_invoice_id = str(external_invoice_id)
            if status_cobranca == StatusCobranca.PAGO:
                cobranca.pago_em = _parse_datetime(_first_value(
                    payload.get("paid_at"), payload.get("paid_at_date"), _nested(payload, ("data", "paid_at"))
                )) or agora
            cobranca.save(update_fields=["status", "ultima_sincronizacao", "dados_gateway", "gateway_charge_id", "gateway_invoice_id", "pago_em", "atualizado_em"])

            payment_status = _status_pagamento(status_cobranca)
            payment_id = _gateway_payment_id(payload)
            payment = None
            if payment_id:
                payment = Pagamento.objects.filter(gateway=provider, gateway_payment_id=str(payment_id)).first()
            if payment_status in {StatusPagamento.PAGO, StatusPagamento.FALHOU, StatusPagamento.ESTORNADO}:
                if payment is not None:
                    payment.status = payment_status
                    if payment_status == StatusPagamento.PAGO:
                        payment.pago_em = cobranca.pago_em
                    elif payment_status == StatusPagamento.FALHOU:
                        payment.falhou_em = timezone.now()
                        payment.motivo_falha = str(_first_value(payload.get("failure_reason"), payload.get("message"), ""))
                    payment.dados_gateway = _sanitizar(payload)
                    payment.save(update_fields=["status", "pago_em", "falhou_em", "motivo_falha", "dados_gateway", "atualizado_em"])
                else:
                    valor = _amount(payload) or cobranca.valor
                    payment = Pagamento.objects.create(
                        cobranca=cobranca,
                        tentativa=(cobranca.pagamentos.order_by("-tentativa").values_list("tentativa", flat=True).first() or 0) + 1,
                        gateway=provider,
                        forma_pagamento=_payment_method(payload),
                        status=payment_status,
                        valor=valor,
                        gateway_payment_id=str(payment_id or _event_id(payload, raw_body)),
                        gateway_transaction_id=str(_nested(payload, ("transaction_id",), ("data", "transaction_id")) or ""),
                        pago_em=cobranca.pago_em if payment_status == StatusPagamento.PAGO else None,
                        falhou_em=timezone.now() if payment_status == StatusPagamento.FALHOU else None,
                        motivo_falha=(str(_first_value(payload.get("failure_reason"), payload.get("message"), "")) if payment_status == StatusPagamento.FALHOU else ""),
                        dados_gateway=_sanitizar(payload),
                    )

        if cobranca and status_cobranca == StatusCobranca.PAGO and cobranca.adesao.status in {StatusAdesao.PENDENTE, StatusAdesao.INADIMPLENTE}:
            cobranca.adesao.status = StatusAdesao.ATIVA
            cobranca.adesao.save(update_fields=["status", "atualizado_em"])

        evento.status = StatusEvento.PROCESSADO
        evento.assinatura_validada = True
        evento.processado_em = timezone.now()
        evento.erro_processamento = ""
        evento.save(update_fields=["adesao", "cobranca", "tentativas", "status", "assinatura_validada", "processado_em", "erro_processamento"])
        _make_audit(evento, f"Webhook {provider} processado: {evento.tipo_evento} ({evento.evento_id}).")
        return {"event_id": evento.evento_id, "status": "processed", "matched": bool(cobranca or adesao)}


def registrar_webhook_rejeitado(provider, payload, raw_body, error):
    with transaction.atomic():
        event_id = _event_id(payload, raw_body)
        existing = EventoGateway.objects.filter(gateway=provider, evento_id=event_id).first()
        if existing and existing.status == StatusEvento.PROCESSADO:
            return existing
        evento, _ = _register_event(provider, payload, raw_body, False, error)
        evento.tentativas = (evento.tentativas or 0) + 1
        evento.status = StatusEvento.ERRO
        evento.erro_processamento = error
        evento.save(update_fields=["tentativas", "status", "erro_processamento"])
        _make_audit(evento, f"Webhook {provider} rejeitado: {error}.", {"evento_id": evento.evento_id, "erro": error})
        return evento


def registrar_webhook_erro(provider, payload, raw_body, error, assinatura_validada=True):
    """Persiste um erro de payload/processamento sem atualizar valores financeiros."""
    with transaction.atomic():
        evento, _ = _register_event(provider, payload, raw_body, assinatura_validada, error)
        evento.tentativas = (evento.tentativas or 0) + 1
        evento.status = StatusEvento.ERRO
        evento.erro_processamento = error
        evento.save(update_fields=["tentativas", "status", "erro_processamento"])
        _make_audit(evento, f"Webhook {provider} registrado com erro: {error}.", {"evento_id": evento.evento_id, "erro": error})
        return evento


def configuracao_gateway_aceita(provider):
    config = GatewayConfiguracao.objects.first()
    return bool(config and config.ativo and config.gateway == provider)
