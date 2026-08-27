from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import render
from django.utils import timezone

from financeiro.models import CobrancaMensalidade, StatusCobranca

from .auth import is_admin


PAINEL_LOGIN = "/usuarios/minha-conta/"
STATUS_ABERTOS = {
    StatusCobranca.PENDENTE,
    StatusCobranca.PROCESSANDO,
    StatusCobranca.VENCIDA,
    StatusCobranca.FALHA,
}
STATUS_RECEBIDOS = {StatusCobranca.PAGO, StatusCobranca.CONCILIACAO_MANUAL}
STATUS_EXCLUIDOS = {StatusCobranca.CANCELADA, StatusCobranca.ESTORNADA}
SITUACOES_VALIDAS = {"todos", "aberto", "pago", "vencido"}


def _primeiro_dia_mes(valor):
    return valor.replace(day=1)


def _meses_anteriores(valor, quantidade):
    indice = valor.year * 12 + (valor.month - 1) - quantidade
    return date(indice // 12, indice % 12 + 1, 1)


def _meses_no_intervalo(inicio, fim):
    cursor = _primeiro_dia_mes(inicio)
    limite = _primeiro_dia_mes(fim)
    meses = []
    while cursor <= limite:
        meses.append(cursor)
        indice = cursor.year * 12 + cursor.month
        cursor = date(indice // 12, indice % 12 + 1, 1)
    return meses


def _ler_data(valor, padrao):
    try:
        return date.fromisoformat(valor) if valor else padrao
    except (TypeError, ValueError):
        return padrao


def _valor_total(queryset):
    return queryset.aggregate(total=Sum("valor"))["total"] or Decimal("0.00")


def _aplicar_situacao(queryset, situacao, hoje):
    if situacao == "aberto":
        return queryset.filter(status__in=STATUS_ABERTOS)
    if situacao == "pago":
        return queryset.filter(status__in=STATUS_RECEBIDOS)
    if situacao == "vencido":
        return queryset.filter(status__in=STATUS_ABERTOS, vencimento__lt=hoje)
    return queryset


def _nome_usuario(usuario):
    return usuario.get_full_name() or usuario.get_username()


def _agrupar_inadimplencia(cobrancas):
    agrupado = {}
    for cobranca in cobrancas:
        usuario = cobranca.adesao.federado
        item = agrupado.setdefault(usuario.pk, {
            "usuario_id": usuario.pk,
            "nome": _nome_usuario(usuario),
            "email": usuario.email,
            "quantidade": 0,
            "total": Decimal("0.00"),
            "vencimento_mais_antigo": cobranca.vencimento,
            "plano": cobranca.adesao.plano.nome,
        })
        item["quantidade"] += 1
        item["total"] += cobranca.valor
        if cobranca.vencimento < item["vencimento_mais_antigo"]:
            item["vencimento_mais_antigo"] = cobranca.vencimento
    return sorted(agrupado.values(), key=lambda item: (-item["total"], item["nome"].lower()))


def _fluxo_mensal(cobrancas, meses):
    por_mes = {
        mes: {"mes": mes, "previsto": Decimal("0.00"), "recebido": Decimal("0.00"), "aberto": Decimal("0.00")}
        for mes in meses
    }
    for cobranca in cobrancas:
        mes_competencia = _primeiro_dia_mes(cobranca.competencia)
        if mes_competencia in por_mes and cobranca.status not in STATUS_EXCLUIDOS:
            por_mes[mes_competencia]["previsto"] += cobranca.valor
            if cobranca.status in STATUS_ABERTOS:
                por_mes[mes_competencia]["aberto"] += cobranca.valor

        if cobranca.status in STATUS_RECEBIDOS:
            mes_recebimento = _primeiro_dia_mes(
                cobranca.pago_em.date() if cobranca.pago_em else cobranca.competencia
            )
            if mes_recebimento in por_mes:
                por_mes[mes_recebimento]["recebido"] += cobranca.valor

    maior = max(
        (max(item["previsto"], item["recebido"], item["aberto"]) for item in por_mes.values()),
        default=Decimal("0.00"),
    ) or Decimal("1.00")
    for item in por_mes.values():
        item["percentual_previsto"] = min(100, float(item["previsto"] / maior * 100))
        item["percentual_recebido"] = min(100, float(item["recebido"] / maior * 100))
        item["percentual_aberto"] = min(100, float(item["aberto"] / maior * 100))
    return list(por_mes.values())


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url=PAINEL_LOGIN)
def relatorio_financeiro(request):
    hoje = timezone.localdate()
    padrao_inicio = _meses_anteriores(_primeiro_dia_mes(hoje), 11)
    inicio = _ler_data(request.GET.get("inicio"), padrao_inicio)
    fim = _ler_data(request.GET.get("fim"), hoje)
    erro_periodo = False
    if inicio > fim:
        inicio, fim = fim, inicio
        erro_periodo = True

    situacao = request.GET.get("situacao", "todos")
    if situacao not in SITUACOES_VALIDAS:
        situacao = "todos"
    busca = request.GET.get("q", "").strip()

    cobrancas_base = CobrancaMensalidade.objects.select_related(
        "adesao__federado", "adesao__plano"
    ).exclude(status__in=STATUS_EXCLUIDOS)
    if busca:
        cobrancas_base = cobrancas_base.filter(
            Q(adesao__federado__username__icontains=busca)
            | Q(adesao__federado__email__icontains=busca)
            | Q(adesao__federado__first_name__icontains=busca)
            | Q(adesao__federado__last_name__icontains=busca)
            | Q(adesao__plano__nome__icontains=busca)
            | Q(gateway_charge_id__icontains=busca)
            | Q(gateway_invoice_id__icontains=busca)
        )

    cobrancas_periodo = cobrancas_base.filter(competencia__range=(inicio, fim))
    cobrancas_filtradas = _aplicar_situacao(cobrancas_periodo, situacao, hoje)
    cobrancas_inadimplentes = cobrancas_periodo.filter(
        status__in=STATUS_ABERTOS,
        vencimento__lt=hoje,
    ).order_by("vencimento", "adesao__federado__last_name", "adesao__federado__first_name")

    total_previsto = _valor_total(cobrancas_filtradas)
    total_recebido = _valor_total(cobrancas_filtradas.filter(status__in=STATUS_RECEBIDOS))
    total_aberto = _valor_total(cobrancas_filtradas.filter(status__in=STATUS_ABERTOS))
    total_vencido = _valor_total(cobrancas_inadimplentes)
    total_com_vencimento = _valor_total(cobrancas_periodo.filter(vencimento__lt=hoje))
    taxa_inadimplencia = float(total_vencido / total_com_vencimento * 100) if total_com_vencimento else 0

    inadimplentes = _agrupar_inadimplencia(cobrancas_inadimplentes)
    inadimplentes_paginados = Paginator(inadimplentes, 15).get_page(request.GET.get("inadimplentes_page"))
    fluxo = _fluxo_mensal(cobrancas_filtradas, _meses_no_intervalo(inicio, fim))

    contexto = {
        "inicio": inicio,
        "fim": fim,
        "hoje": hoje,
        "situacao": situacao,
        "busca": busca,
        "erro_periodo": erro_periodo,
        "total_previsto": total_previsto,
        "total_recebido": total_recebido,
        "total_aberto": total_aberto,
        "total_vencido": total_vencido,
        "qtd_cobrancas": cobrancas_filtradas.count(),
        "qtd_inadimplentes": len(inadimplentes),
        "qtd_cobrancas_vencidas": cobrancas_inadimplentes.count(),
        "taxa_inadimplencia": taxa_inadimplencia,
        "fluxo": fluxo,
        "inadimplentes": inadimplentes_paginados,
    }
    return render(request, "painel/financeiro/relatorio.html", contexto)
