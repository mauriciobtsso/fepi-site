from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


class AssistenteEManualTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser(
            username="admin-ia",
            email="admin-ia@example.com",
            password="senha-segura-ia",
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def test_manual_financeiro_exige_admin_e_exibe_conteudo(self):
        response = self.client.get(reverse("manual_financeiro"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manual do módulo financeiro")
        self.assertContains(response, "Como cadastrar um federado ou associado")
        self.assertContains(response, "FormaDoacao")

    @override_settings(GEMINI_API_KEY="", GROQ_API_KEY="")
    def test_assistente_retorna_indisponibilidade_sem_credenciais(self):
        response = self.client.post(
            reverse("assistente_ia"),
            data={"mensagem": "Como cadastrar um plano?"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 503)
        self.assertIn("temporariamente indisponível", response.json()["erro"])

    def test_assistente_rejeita_mensagem_vazia(self):
        response = self.client.post(
            reverse("assistente_ia"),
            data={"mensagem": "   "},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    @override_settings(GEMINI_API_KEY="gemini-teste", GROQ_API_KEY="")
    @patch("painel.views.ia_views.google_genai.Client")
    def test_assistente_usa_gemini_valido_e_manual_em_duvida_financeira(self, client_class):
        cliente = Mock()
        cliente.models.generate_content.return_value = SimpleNamespace(text="Use Financeiro > Novo plano.")
        client_class.return_value = cliente

        response = self.client.post(
            reverse("assistente_ia"),
            data={"mensagem": "Como cadastrar um plano de mensalidade?"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["provedor"], "gemini")
        chamada = cliente.models.generate_content.call_args.kwargs
        self.assertEqual(chamada["model"], "gemini-3-flash-preview")
        self.assertIn("Manual do módulo financeiro", chamada["contents"])
        client_class.assert_called_once()
        opcoes_http = client_class.call_args.kwargs["http_options"]
        self.assertEqual(opcoes_http["timeout"], 30000)
        self.assertEqual(opcoes_http["retry_options"]["attempts"], 2)

    @override_settings(GEMINI_API_KEY="gemini-teste", GROQ_API_KEY="groq-teste")
    @patch("painel.views.ia_views.Groq")
    @patch("painel.views.ia_views.google_genai.Client")
    def test_assistente_faz_fallback_para_groq_sem_expor_erro_tecnico(self, client_class, groq_class):
        cliente_google = Mock()
        cliente_google.models.generate_content.side_effect = RuntimeError("falha de transporte")
        client_class.return_value = cliente_google

        cliente_groq = Mock()
        cliente_groq.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Resposta de contingência."))]
        )
        groq_class.return_value = cliente_groq

        response = self.client.post(
            reverse("assistente_ia"),
            data={"mensagem": "Explique o Editor.js."},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["provedor"], "groq")
        self.assertTrue(response.json()["fallback"])
        groq_class.assert_called_once_with(api_key="groq-teste", timeout=25.0, max_retries=1)

    @override_settings(AI_MAX_MESSAGE_CHARS=500, GEMINI_API_KEY="gemini-teste", GROQ_API_KEY="")
    def test_assistente_aplica_limite_de_mensagem(self):
        response = self.client.post(
            reverse("assistente_ia"),
            data={"mensagem": "x" * 501},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 413)
