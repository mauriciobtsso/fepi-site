from datetime import date, timedelta
from decimal import Decimal
import hashlib
import hmac
import json

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from financeiro.admin import PlanoMensalidadeAdmin
from painel.forms.financeiro import PlanoMensalidadeForm

from .models import (
    AcaoAuditoria,
    AdesaoMensalidade,
    AmbienteGateway,
    AuditoriaFinanceira,
    CobrancaMensalidade,
    EventoGateway,
    FormaPagamento,
    Gateway,
    GatewayConfiguracao,
    Pagamento,
    PlanoMensalidade,
    StatusAdesao,
    StatusCobranca,
    StatusConexaoGateway,
    StatusEvento,
    StatusPagamento,
)


class FinanceiroModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="federado-modelo",
            email="federado-modelo@example.com",
        )
        cls.plano = PlanoMensalidade.objects.create(
            slug="contribuinte-base",
            nome="Contribuinte Base",
            valor=Decimal("35.00"),
            dia_vencimento=10,
            gateway=Gateway.PAGBANK,
        )
        cls.adesao = AdesaoMensalidade.objects.create(
            federado=cls.usuario,
            plano=cls.plano,
            forma_pagamento=FormaPagamento.BOLETO,
            valor_contratado=Decimal("35.00"),
            dia_vencimento=10,
            gateway=Gateway.PAGBANK,
        )

    def test_cobranca_tem_uma_unica_competencia_por_adesao(self):
        competencia = date(2026, 8, 1)
        CobrancaMensalidade.objects.create(
            adesao=self.adesao,
            competencia=competencia,
            vencimento=date(2026, 8, 10),
            valor=Decimal("35.00"),
            forma_pagamento=FormaPagamento.BOLETO,
            gateway=Gateway.PAGBANK,
        )

        with self.assertRaises(IntegrityError):
            CobrancaMensalidade.objects.create(
                adesao=self.adesao,
                competencia=competencia,
                vencimento=date(2026, 8, 10),
                valor=Decimal("35.00"),
                forma_pagamento=FormaPagamento.BOLETO,
                gateway=Gateway.PAGBANK,
            )

    def test_cobranca_pendente_vencida_expoe_propriedade(self):
        cobranca = CobrancaMensalidade.objects.create(
            adesao=self.adesao,
            competencia=date(2020, 1, 1),
            vencimento=timezone.localdate() - timedelta(days=1),
            valor=Decimal("35.00"),
            forma_pagamento=FormaPagamento.BOLETO,
            gateway=Gateway.PAGBANK,
            status=StatusCobranca.PENDENTE,
        )
        self.assertTrue(cobranca.esta_vencida)

    def test_evento_de_gateway_e_idempotente_por_gateway_e_id(self):
        EventoGateway.objects.create(
            gateway=Gateway.PAGBANK,
            evento_id="evt-teste-001",
            tipo_evento="charge.paid",
            payload={"id": "evt-teste-001"},
        )

        with self.assertRaises(IntegrityError):
            EventoGateway.objects.create(
                gateway=Gateway.PAGBANK,
                evento_id="evt-teste-001",
                tipo_evento="charge.paid",
                payload={"id": "evt-teste-001"},
            )

    def test_mesmo_evento_pode_existir_em_gateways_diferentes(self):
        EventoGateway.objects.create(
            gateway=Gateway.PAGBANK,
            evento_id="evt-compartilhado",
            tipo_evento="charge.paid",
            payload={},
        )
        EventoGateway.objects.create(
            gateway=Gateway.PAGARME,
            evento_id="evt-compartilhado",
            tipo_evento="charge.paid",
            payload={},
        )
        self.assertEqual(EventoGateway.objects.filter(evento_id="evt-compartilhado").count(), 2)


class FinanceiroPainelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser(
            username="admin-financeiro",
            email="admin-financeiro@example.com",
            password="senha-segura-teste",
        )
        cls.federado_sem_acesso = get_user_model().objects.create_user(
            username="federado-sem-area",
            email="sem-area@example.com",
            is_active=False,
        )
        cls.plano = PlanoMensalidade.objects.create(
            slug="plano-painel",
            nome="Plano do painel",
            valor=Decimal("25.00"),
            dia_vencimento=15,
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def test_hub_financeiro_exige_administrador(self):
        response = self.client.get(reverse("financeiro_hub"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gestão de mensalidades")

    def test_admin_pode_criar_plano_e_auditoria_e_gerada(self):
        response = self.client.post(reverse("novo_plano_financeiro"), {
            "nome": "Plano Solidário",
            "slug": "plano-solidario",
            "descricao": "Contribuição mensal.",
            "valor": "40.00",
            "dia_vencimento": "10",
            "gateway": Gateway.NENHUM,
            "gateway_plan_id": "",
            "ativo": "on",
        })
        self.assertRedirects(response, reverse("financeiro_hub"))
        plano = PlanoMensalidade.objects.get(slug="plano-solidario")
        self.assertTrue(AuditoriaFinanceira.objects.filter(
            content_type=ContentType.objects.get_for_model(plano),
            object_id=plano.pk,
            usuario=self.admin,
            acao=AcaoAuditoria.CRIACAO,
        ).exists())

    def test_admin_pode_associar_usuario_inativo_sem_area_do_federado(self):
        response = self.client.post(reverse("nova_adesao_financeira"), {
            "federado": self.federado_sem_acesso.pk,
            "plano": self.plano.pk,
            "status": StatusAdesao.PENDENTE,
            "forma_pagamento": FormaPagamento.BOLETO,
            "valor_contratado": "25.00",
            "dia_vencimento": "15",
            "data_inicio": "2026-08-01",
            "data_fim": "",
            "proxima_cobranca": "",
            "gateway": Gateway.NENHUM,
            "gateway_customer_id": "",
            "gateway_subscription_id": "",
            "gateway_reference": "",
            "observacoes": "",
        })
        self.assertRedirects(response, reverse("financeiro_hub"))
        adesao = AdesaoMensalidade.objects.get(federado=self.federado_sem_acesso)
        self.assertEqual(adesao.valor_contratado, Decimal("25.00"))
        self.assertTrue(AuditoriaFinanceira.objects.filter(
            content_type=ContentType.objects.get_for_model(adesao),
            object_id=adesao.pk,
            usuario=self.admin,
            acao=AcaoAuditoria.CRIACAO,
        ).exists())

    def test_admin_pode_criar_e_alternar_gateway_sem_persistir_segredos(self):
        dados_base = {
            "gateway": Gateway.PAGBANK,
            "ambiente": AmbienteGateway.SANDBOX,
            "ativo": "",
            "aceita_cartao": "on",
            "aceita_boleto": "on",
            "aceita_pix": "on",
            "webhook_url": "",
            "observacoes": "Homologação inicial.",
        }
        response = self.client.post(reverse("gerenciar_configuracao_gateway"), dados_base)
        self.assertRedirects(response, reverse("financeiro_hub"))
        config = GatewayConfiguracao.objects.get()
        self.assertEqual(config.gateway, Gateway.PAGBANK)
        self.assertEqual(config.status_conexao, StatusConexaoGateway.NAO_TESTADO)
        self.assertEqual(config.atualizado_por, self.admin)
        self.assertFalse(hasattr(config, "access_token"))

        dados_base.update({
            "gateway": Gateway.PAGARME,
            "ambiente": AmbienteGateway.PRODUCAO,
            "ativo": "on",
        })
        response = self.client.post(reverse("gerenciar_configuracao_gateway"), dados_base)
        self.assertRedirects(response, reverse("financeiro_hub"))
        config.refresh_from_db()
        self.assertEqual(config.gateway, Gateway.PAGARME)
        self.assertEqual(config.ambiente, AmbienteGateway.PRODUCAO)
        self.assertTrue(config.ativo)
        self.assertEqual(config.status_conexao, StatusConexaoGateway.NAO_TESTADO)
        self.assertEqual(AuditoriaFinanceira.objects.filter(object_id=config.pk).count(), 2)

    def test_formulario_gateway_renderiza_sem_campos_de_segredo(self):
        response = self.client.get(reverse("gerenciar_configuracao_gateway"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PagBank")
        self.assertContains(response, "Pagar.me")
        self.assertNotContains(response, "PAGBANK_ACCESS_TOKEN")
        self.assertNotContains(response, "PAGARME_API_KEY")

    def test_formularios_financeiros_renderizam(self):
        for nome_url in ("novo_plano_financeiro", "nova_adesao_financeira", "nova_cobranca_financeira"):
            with self.subTest(url=nome_url):
                response = self.client.get(reverse(nome_url))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Salvar e registrar histórico")

    def test_salvamento_direto_no_django_admin_gera_auditoria(self):
        plano = PlanoMensalidade.objects.get(pk=self.plano.pk)
        plano.nome = "Plano do painel atualizado"
        form = PlanoMensalidadeForm(instance=plano, data={
            "nome": plano.nome,
            "slug": plano.slug,
            "descricao": plano.descricao,
            "valor": "25.00",
            "dia_vencimento": "15",
            "gateway": plano.gateway,
            "gateway_plan_id": plano.gateway_plan_id,
            "ativo": "on",
        })
        self.assertTrue(form.is_valid(), form.errors)
        request = RequestFactory().post("/admin/financeiro/planomensalidade/")
        request.user = self.admin
        PlanoMensalidadeAdmin(PlanoMensalidade, admin.site).save_model(request, plano, form, change=True)
        self.assertTrue(AuditoriaFinanceira.objects.filter(
            content_type=ContentType.objects.get_for_model(plano),
            object_id=plano.pk,
            usuario=self.admin,
            acao=AcaoAuditoria.ALTERACAO,
        ).exists())

    @override_settings(PAGBANK_WEBHOOK_TOKEN="token-pagbank-teste")
    def test_webhook_pagbank_autentica_processa_e_e_idempotente(self):
        self.plano.gateway = Gateway.PAGBANK
        self.plano.save(update_fields=["gateway", "atualizado_em"])
        adesao = AdesaoMensalidade.objects.create(
            federado=self.federado_sem_acesso,
            plano=self.plano,
            forma_pagamento=FormaPagamento.PIX,
            valor_contratado=Decimal("25.00"),
            dia_vencimento=15,
            gateway=Gateway.PAGBANK,
            gateway_reference="adesao-pagbank-1",
        )
        cobranca = CobrancaMensalidade.objects.create(
            adesao=adesao,
            competencia=date(2026, 8, 1),
            vencimento=date(2026, 8, 15),
            valor=Decimal("25.00"),
            forma_pagamento=FormaPagamento.PIX,
            gateway=Gateway.PAGBANK,
            gateway_charge_id="CH_PAGBANK_001",
        )
        GatewayConfiguracao.objects.create(gateway=Gateway.PAGBANK, ativo=True)
        payload = {
            "id": "evt-pagbank-001",
            "status": "PAID",
            "charge_id": "CH_PAGBANK_001",
            "amount": {"value": 2500},
            "payment_method": {"type": "PIX"},
        }
        body = json.dumps(payload, separators=(",", ":")).encode()
        assinatura = hashlib.sha256(b"token-pagbank-teste-" + body).hexdigest()
        url = reverse("gateway_webhook", kwargs={"gateway": "pagbank"})

        response = self.client.post(url, body, content_type="application/json", HTTP_X_AUTHENTICITY_TOKEN=assinatura)
        self.assertEqual(response.status_code, 200)
        cobranca.refresh_from_db()
        adesao.refresh_from_db()
        self.assertEqual(cobranca.status, StatusCobranca.PAGO)
        self.assertEqual(cobranca.pagamentos.count(), 1)
        self.assertEqual(cobranca.pagamentos.get().status, StatusPagamento.PAGO)
        self.assertEqual(adesao.status, StatusAdesao.ATIVA)
        evento = EventoGateway.objects.get(evento_id="evt-pagbank-001")
        self.assertEqual(evento.status, StatusEvento.PROCESSADO)
        self.assertTrue(evento.assinatura_validada)

        response = self.client.post(url, body, content_type="application/json", HTTP_X_AUTHENTICITY_TOKEN=assinatura)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cobranca.pagamentos.count(), 1)

    @override_settings(PAGBANK_WEBHOOK_TOKEN="token-pagbank-teste")
    def test_webhook_pagbank_rejeita_assinatura_invalida_sem_baixar_cobranca(self):
        GatewayConfiguracao.objects.create(gateway=Gateway.PAGBANK, ativo=True)
        payload = {"id": "evt-pagbank-invalido", "status": "PAID", "charge_id": "CH_INEXISTENTE"}
        body = json.dumps(payload).encode()
        response = self.client.post(
            reverse("gateway_webhook", kwargs={"gateway": "pagbank"}),
            body,
            content_type="application/json",
            HTTP_X_AUTHENTICITY_TOKEN="assinatura-errada",
        )
        self.assertEqual(response.status_code, 401)
        evento = EventoGateway.objects.get(evento_id="evt-pagbank-invalido")
        self.assertEqual(evento.status, StatusEvento.ERRO)
        self.assertFalse(evento.assinatura_validada)

    @override_settings(PAGARME_WEBHOOK_SECRET="segredo-pagarme-teste")
    def test_webhook_pagarme_processa_cobranca_por_hmac(self):
        self.plano.gateway = Gateway.PAGARME
        self.plano.save(update_fields=["gateway", "atualizado_em"])
        adesao = AdesaoMensalidade.objects.create(
            federado=self.federado_sem_acesso,
            plano=self.plano,
            forma_pagamento=FormaPagamento.BOLETO,
            valor_contratado=Decimal("25.00"),
            dia_vencimento=15,
            gateway=Gateway.PAGARME,
        )
        cobranca = CobrancaMensalidade.objects.create(
            adesao=adesao,
            competencia=date(2026, 8, 1),
            vencimento=date(2026, 8, 15),
            valor=Decimal("25.00"),
            forma_pagamento=FormaPagamento.BOLETO,
            gateway=Gateway.PAGARME,
            gateway_charge_id="CH_PAGARME_001",
        )
        GatewayConfiguracao.objects.create(gateway=Gateway.PAGARME, ativo=True)
        payload = {
            "id": "evt-pagarme-001",
            "event": "charge.paid",
            "data": {"id": "CH_PAGARME_001", "amount": 2500, "payment_method": "boleto"},
        }
        body = json.dumps(payload, separators=(",", ":")).encode()
        assinatura = hmac.new(b"segredo-pagarme-teste", body, hashlib.sha256).hexdigest()
        response = self.client.post(
            reverse("gateway_webhook", kwargs={"gateway": "pagarme"}),
            body,
            content_type="application/json",
            HTTP_X_PAGARME_SIGNATURE=assinatura,
        )
        self.assertEqual(response.status_code, 200)
        cobranca.refresh_from_db()
        self.assertEqual(cobranca.status, StatusCobranca.PAGO)
        self.assertEqual(cobranca.pagamentos.get().valor, Decimal("25.00"))

    def test_historico_financeiro_lista_movimentacoes(self):
        auditoria = AuditoriaFinanceira.objects.create(
            usuario=self.admin,
            acao=AcaoAuditoria.ALTERACAO,
            content_type=ContentType.objects.get_for_model(self.plano),
            object_id=self.plano.pk,
            descricao="Teste de histórico",
            dados_anteriores={"valor": "20.00"},
            dados_novos={"valor": "25.00"},
        )
        response = self.client.get(reverse("listar_auditoria_financeira"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, auditoria.descricao)
