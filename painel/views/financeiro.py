import json

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from financeiro.models import (
    AcaoAuditoria,
    AdesaoMensalidade,
    AuditoriaFinanceira,
    CobrancaMensalidade,
    StatusAdesao,
    StatusCobranca,
    PlanoMensalidade,
)
from painel.forms.financeiro import (
    AdesaoMensalidadeForm,
    CobrancaMensalidadeForm,
    PlanoMensalidadeForm,
)

from .auth import is_admin


PAINEL_LOGIN = "/usuarios/minha-conta/"


def _json_snapshot(instance):
    """Cria um snapshot serializável dos campos concretos do modelo."""
    dados = {}
    for field in instance._meta.concrete_fields:
        value = getattr(instance, field.attname)
        if hasattr(value, "name"):
            value = value.name
        dados[field.name] = value
    return json.loads(json.dumps(dados, cls=DjangoJSONEncoder))


def _registrar_auditoria(usuario, objeto, acao, descricao, antes=None, depois=None):
    return AuditoriaFinanceira.objects.create(
        usuario=usuario,
        acao=acao,
        content_type=ContentType.objects.get_for_model(objeto),
        object_id=objeto.pk,
        descricao=descricao,
        dados_anteriores=antes or {},
        dados_novos=depois or _json_snapshot(objeto),
    )


def _acao_para_alteracao(antes, depois, padrao=AcaoAuditoria.ALTERACAO):
    if antes and depois and antes.get("status") != depois.get("status"):
        novo_status = depois.get("status")
        if novo_status in {StatusAdesao.CANCELADA, StatusCobranca.CANCELADA}:
            return AcaoAuditoria.CANCELAMENTO
        if novo_status == StatusAdesao.SUSPENSA:
            return AcaoAuditoria.SUSPENSAO
        if novo_status in {StatusAdesao.ATIVA, StatusCobranca.PAGO, StatusCobranca.CONCILIACAO_MANUAL}:
            return AcaoAuditoria.BAIXA_MANUAL if novo_status != StatusAdesao.ATIVA else AcaoAuditoria.ATIVACAO
    return padrao


def _paginar(request, queryset, por_pagina=15):
    return Paginator(queryset, por_pagina).get_page(request.GET.get("page"))


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url=PAINEL_LOGIN)
def financeiro_hub(request):
    query = request.GET.get("q", "").strip()
    plano_qs = PlanoMensalidade.objects.all()
    adesao_qs = AdesaoMensalidade.objects.select_related("federado", "plano")
    cobranca_qs = CobrancaMensalidade.objects.select_related("adesao__federado", "adesao__plano")

    if query:
        plano_qs = plano_qs.filter(Q(nome__icontains=query) | Q(slug__icontains=query))
        adesao_qs = adesao_qs.filter(
            Q(federado__username__icontains=query)
            | Q(federado__email__icontains=query)
            | Q(federado__first_name__icontains=query)
            | Q(federado__last_name__icontains=query)
            | Q(plano__nome__icontains=query)
        )
        cobranca_qs = cobranca_qs.filter(
            Q(adesao__federado__username__icontains=query)
            | Q(adesao__federado__email__icontains=query)
            | Q(adesao__federado__first_name__icontains=query)
            | Q(adesao__federado__last_name__icontains=query)
            | Q(gateway_charge_id__icontains=query)
            | Q(gateway_invoice_id__icontains=query)
        )

    contexto = {
        "query": query,
        "planos": _paginar(request, plano_qs.order_by("nome"), 8),
        "adesoes": _paginar(request, adesao_qs.order_by("-criado_em"), 12),
        "cobrancas": _paginar(request, cobranca_qs.order_by("-competencia", "-criado_em"), 12),
        "total_planos": PlanoMensalidade.objects.count(),
        "planos_ativos": PlanoMensalidade.objects.filter(ativo=True).count(),
        "adesoes_ativas": AdesaoMensalidade.objects.filter(status=StatusAdesao.ATIVA).count(),
        "cobrancas_pendentes": CobrancaMensalidade.objects.filter(
            status__in=[StatusCobranca.PENDENTE, StatusCobranca.VENCIDA]
        ).count(),
        "cobrancas_pagas": CobrancaMensalidade.objects.filter(status=StatusCobranca.PAGO).count(),
    }
    return render(request, "painel/financeiro/hub.html", contexto)


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url=PAINEL_LOGIN)
def gerenciar_plano_financeiro(request, id=None):
    instancia = get_object_or_404(PlanoMensalidade, pk=id) if id else None
    antes = _json_snapshot(instancia) if instancia else {}

    if request.method == "POST":
        form = PlanoMensalidadeForm(request.POST, instance=instancia)
        if form.is_valid():
            with transaction.atomic():
                plano = form.save()
                depois = _json_snapshot(plano)
                acao = AcaoAuditoria.ALTERACAO if instancia else AcaoAuditoria.CRIACAO
                descricao = (
                    f"Plano '{plano.nome}' atualizado pelo painel."
                    if instancia
                    else f"Plano '{plano.nome}' criado pelo painel."
                )
                _registrar_auditoria(request.user, plano, acao, descricao, antes, depois)
            messages.success(request, "Plano de mensalidade salvo e registrado no histórico.")
            return redirect("financeiro_hub")
    else:
        form = PlanoMensalidadeForm(instance=instancia)

    return render(request, "painel/financeiro/form.html", {
        "form": form,
        "titulo": "Editar plano de mensalidade" if instancia else "Novo plano de mensalidade",
        "subtitulo": "Defina o valor, o vencimento e a futura referência do gateway.",
        "icone": "fa-layer-group",
        "voltar_url": "financeiro_hub",
    })


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url=PAINEL_LOGIN)
def gerenciar_adesao_financeira(request, id=None):
    instancia = get_object_or_404(AdesaoMensalidade, pk=id) if id else None
    antes = _json_snapshot(instancia) if instancia else {}

    if request.method == "POST":
        form = AdesaoMensalidadeForm(request.POST, instance=instancia)
        if form.is_valid():
            with transaction.atomic():
                adesao = form.save()
                depois = _json_snapshot(adesao)
                acao = _acao_para_alteracao(antes, depois) if instancia else AcaoAuditoria.CRIACAO
                nome = adesao.federado.get_full_name() or adesao.federado.get_username()
                descricao = (
                    f"Adesão de {nome} ao plano '{adesao.plano.nome}' atualizada pelo painel."
                    if instancia
                    else f"Adesão de {nome} ao plano '{adesao.plano.nome}' criada pelo painel."
                )
                _registrar_auditoria(request.user, adesao, acao, descricao, antes, depois)
            messages.success(request, "Adesão salva e registrada no histórico.")
            return redirect("financeiro_hub")
    else:
        form = AdesaoMensalidadeForm(instance=instancia)

    return render(request, "painel/financeiro/form.html", {
        "form": form,
        "titulo": "Editar adesão" if instancia else "Associar federado a um plano",
        "subtitulo": "A associação aceita qualquer usuário cadastrado, mesmo sem acesso à Área do Federado.",
        "icone": "fa-user-check",
        "voltar_url": "financeiro_hub",
    })


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url=PAINEL_LOGIN)
def gerenciar_cobranca_financeira(request, id=None):
    instancia = get_object_or_404(CobrancaMensalidade, pk=id) if id else None
    antes = _json_snapshot(instancia) if instancia else {}

    if request.method == "POST":
        form = CobrancaMensalidadeForm(request.POST, instance=instancia)
        if form.is_valid():
            with transaction.atomic():
                cobranca = form.save()
                depois = _json_snapshot(cobranca)
                acao = _acao_para_alteracao(antes, depois) if instancia else AcaoAuditoria.CRIACAO
                descricao = (
                    f"Cobrança da competência {cobranca.competencia:%m/%Y} atualizada pelo painel."
                    if instancia
                    else f"Cobrança da competência {cobranca.competencia:%m/%Y} criada pelo painel."
                )
                _registrar_auditoria(request.user, cobranca, acao, descricao, antes, depois)
            messages.success(request, "Cobrança salva e registrada no histórico.")
            return redirect("financeiro_hub")
    else:
        form = CobrancaMensalidadeForm(instance=instancia)

    return render(request, "painel/financeiro/form.html", {
        "form": form,
        "titulo": "Editar cobrança" if instancia else "Registrar cobrança",
        "subtitulo": "Use esta tela para preparar ou registrar uma cobrança; o gateway ainda não está conectado.",
        "icone": "fa-receipt",
        "voltar_url": "financeiro_hub",
    })


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url=PAINEL_LOGIN)
def listar_auditoria_financeira(request):
    query = request.GET.get("q", "").strip()
    auditorias = AuditoriaFinanceira.objects.select_related("usuario", "content_type")
    if query:
        auditorias = auditorias.filter(
            Q(descricao__icontains=query)
            | Q(usuario__username__icontains=query)
            | Q(usuario__email__icontains=query)
            | Q(acao__icontains=query)
        )
    return render(request, "painel/financeiro/auditoria.html", {
        "auditorias": _paginar(request, auditorias.order_by("-criado_em"), 25),
        "query": query,
    })
