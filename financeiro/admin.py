from django.contrib import admin

from .models import (
    AdesaoMensalidade,
    AuditoriaFinanceira,
    CobrancaMensalidade,
    EventoGateway,
    Pagamento,
    PlanoMensalidade,
)


@admin.register(PlanoMensalidade)
class PlanoMensalidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "valor", "dia_vencimento", "gateway", "ativo", "atualizado_em")
    list_filter = ("ativo", "gateway")
    search_fields = ("nome", "slug", "gateway_plan_id")
    prepopulated_fields = {"slug": ("nome",)}
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(AdesaoMensalidade)
class AdesaoMensalidadeAdmin(admin.ModelAdmin):
    list_display = (
        "federado",
        "plano",
        "valor_contratado",
        "forma_pagamento",
        "status",
        "proxima_cobranca",
        "gateway",
    )
    list_filter = ("status", "forma_pagamento", "gateway", "plano")
    search_fields = (
        "federado__username",
        "federado__email",
        "federado__first_name",
        "federado__last_name",
        "gateway_customer_id",
        "gateway_subscription_id",
    )
    raw_id_fields = ("federado",)
    readonly_fields = ("criado_em", "atualizado_em")
    date_hierarchy = "data_inicio"


@admin.register(CobrancaMensalidade)
class CobrancaMensalidadeAdmin(admin.ModelAdmin):
    list_display = (
        "federado",
        "competencia",
        "vencimento",
        "valor",
        "status",
        "forma_pagamento",
        "gateway",
        "pago_em",
    )
    list_filter = ("status", "forma_pagamento", "gateway")
    search_fields = (
        "adesao__federado__username",
        "adesao__federado__email",
        "adesao__federado__first_name",
        "adesao__federado__last_name",
        "gateway_invoice_id",
        "gateway_charge_id",
        "codigo_barras",
    )
    raw_id_fields = ("adesao",)
    readonly_fields = ("criado_em", "atualizado_em", "ultima_sincronizacao")
    date_hierarchy = "competencia"

    @admin.display(description="Federado", ordering="adesao__federado__username")
    def federado(self, obj):
        return obj.adesao.federado.get_full_name() or obj.adesao.federado.get_username()


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cobranca",
        "tentativa",
        "valor",
        "forma_pagamento",
        "status",
        "gateway",
        "pago_em",
    )
    list_filter = ("status", "forma_pagamento", "gateway")
    search_fields = (
        "gateway_payment_id",
        "gateway_transaction_id",
        "cobranca__adesao__federado__username",
        "cobranca__adesao__federado__email",
    )
    raw_id_fields = ("cobranca",)
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(EventoGateway)
class EventoGatewayAdmin(admin.ModelAdmin):
    list_display = (
        "gateway",
        "tipo_evento",
        "evento_id",
        "status",
        "assinatura_validada",
        "tentativas",
        "recebido_em",
        "processado_em",
    )
    list_filter = ("gateway", "status", "assinatura_validada", "tipo_evento")
    search_fields = ("evento_id", "tipo_evento", "adesao__gateway_subscription_id", "cobranca__gateway_charge_id")
    raw_id_fields = ("adesao", "cobranca")
    readonly_fields = tuple(field.name for field in EventoGateway._meta.fields)
    date_hierarchy = "recebido_em"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AuditoriaFinanceira)
class AuditoriaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ("acao", "descricao", "usuario", "content_type", "object_id", "criado_em")
    list_filter = ("acao", "content_type")
    search_fields = ("descricao", "usuario__username", "usuario__email")
    raw_id_fields = ("usuario",)
    readonly_fields = tuple(field.name for field in AuditoriaFinanceira._meta.fields)
    date_hierarchy = "criado_em"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
