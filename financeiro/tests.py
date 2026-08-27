from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from .models import (
    CobrancaMensalidade,
    EventoGateway,
    FormaPagamento,
    Gateway,
    PlanoMensalidade,
    StatusCobranca,
)
from .models import AdesaoMensalidade


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
