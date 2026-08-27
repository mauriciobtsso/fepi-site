from django import forms
from django.contrib.auth import get_user_model

from financeiro.models import (
    AdesaoMensalidade,
    CobrancaMensalidade,
    GatewayConfiguracao,
    PlanoMensalidade,
)


User = get_user_model()


class FederadoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        nome = obj.get_full_name().strip()
        identificacao = nome or obj.username
        if obj.email:
            identificacao = f"{identificacao} — {obj.email}"
        if not obj.is_active:
            identificacao = f"{identificacao} (acesso inativo)"
        return identificacao


class GatewayConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = GatewayConfiguracao
        fields = [
            "gateway",
            "ambiente",
            "ativo",
            "aceita_cartao",
            "aceita_boleto",
            "aceita_pix",
            "webhook_url",
            "observacoes",
        ]
        widgets = {
            "gateway": forms.Select(attrs={"class": "form-select"}),
            "ambiente": forms.Select(attrs={"class": "form-select"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "aceita_cartao": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "aceita_boleto": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "aceita_pix": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "webhook_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://.../financeiro/webhooks/..."}),
            "observacoes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class PlanoMensalidadeForm(forms.ModelForm):
    class Meta:
        model = PlanoMensalidade
        fields = [
            "nome",
            "slug",
            "descricao",
            "valor",
            "dia_vencimento",
            "gateway",
            "gateway_plan_id",
            "ativo",
        ]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex.: Contribuinte mensal"}),
            "slug": forms.TextInput(attrs={"class": "form-control", "placeholder": "contribuinte-mensal"}),
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "valor": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "dia_vencimento": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "28"}),
            "gateway": forms.Select(attrs={"class": "form-select"}),
            "gateway_plan_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "Preencher após homologação"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class AdesaoMensalidadeForm(forms.ModelForm):
    federado = FederadoChoiceField(
        queryset=User.objects.all().order_by("first_name", "last_name", "username"),
        label="Federado / usuário cadastrado",
        help_text="A associação pode ser feita mesmo que o usuário esteja sem acesso à Área do Federado.",
    )

    class Meta:
        model = AdesaoMensalidade
        fields = [
            "federado",
            "plano",
            "status",
            "forma_pagamento",
            "valor_contratado",
            "dia_vencimento",
            "data_inicio",
            "data_fim",
            "proxima_cobranca",
            "gateway",
            "gateway_customer_id",
            "gateway_subscription_id",
            "gateway_reference",
            "observacoes",
        ]
        widgets = {
            "plano": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "forma_pagamento": forms.Select(attrs={"class": "form-select"}),
            "valor_contratado": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "dia_vencimento": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "28"}),
            "data_inicio": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "data_fim": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "proxima_cobranca": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "gateway": forms.Select(attrs={"class": "form-select"}),
            "gateway_customer_id": forms.TextInput(attrs={"class": "form-control"}),
            "gateway_subscription_id": forms.TextInput(attrs={"class": "form-control"}),
            "gateway_reference": forms.TextInput(attrs={"class": "form-control"}),
            "observacoes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["plano"].queryset = PlanoMensalidade.objects.order_by("nome")
        if not self.instance.pk:
            self.fields["valor_contratado"].required = False
            self.fields["dia_vencimento"].required = False

    def clean(self):
        cleaned_data = super().clean()
        plano = cleaned_data.get("plano")
        if plano:
            if cleaned_data.get("valor_contratado") in (None, ""):
                cleaned_data["valor_contratado"] = plano.valor
            if cleaned_data.get("dia_vencimento") in (None, ""):
                cleaned_data["dia_vencimento"] = plano.dia_vencimento
        if cleaned_data.get("valor_contratado") is None:
            self.add_error("valor_contratado", "Informe o valor contratado ou selecione um plano com valor definido.")
        if cleaned_data.get("dia_vencimento") is None:
            self.add_error("dia_vencimento", "Informe o dia de vencimento ou selecione um plano.")
        return cleaned_data


class CobrancaMensalidadeForm(forms.ModelForm):
    class Meta:
        model = CobrancaMensalidade
        fields = [
            "adesao",
            "competencia",
            "vencimento",
            "valor",
            "status",
            "forma_pagamento",
            "gateway",
            "gateway_invoice_id",
            "gateway_charge_id",
            "url_pagamento",
            "url_boleto",
            "codigo_barras",
            "pix_copia_cola",
            "pix_expira_em",
            "nome_pagador",
            "documento_pagador",
            "email_pagador",
            "telefone_pagador",
            "pago_em",
            "observacoes",
        ]
        widgets = {
            "adesao": forms.Select(attrs={"class": "form-select"}),
            "competencia": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "vencimento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "valor": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "forma_pagamento": forms.Select(attrs={"class": "form-select"}),
            "gateway": forms.Select(attrs={"class": "form-select"}),
            "gateway_invoice_id": forms.TextInput(attrs={"class": "form-control"}),
            "gateway_charge_id": forms.TextInput(attrs={"class": "form-control"}),
            "url_pagamento": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
            "url_boleto": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
            "codigo_barras": forms.TextInput(attrs={"class": "form-control"}),
            "pix_copia_cola": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "pix_expira_em": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "nome_pagador": forms.TextInput(attrs={"class": "form-control"}),
            "documento_pagador": forms.TextInput(attrs={"class": "form-control"}),
            "email_pagador": forms.EmailInput(attrs={"class": "form-control"}),
            "telefone_pagador": forms.TextInput(attrs={"class": "form-control"}),
            "pago_em": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "observacoes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["adesao"].queryset = (
            AdesaoMensalidade.objects.select_related("federado", "plano")
            .order_by("federado__first_name", "federado__last_name", "federado__username")
        )
        if not self.instance.pk:
            self.fields["valor"].required = False

    def clean(self):
        cleaned_data = super().clean()
        adesao = cleaned_data.get("adesao")
        if adesao:
            if cleaned_data.get("valor") in (None, ""):
                cleaned_data["valor"] = adesao.valor_contratado
            if not cleaned_data.get("nome_pagador"):
                cleaned_data["nome_pagador"] = adesao.federado.get_full_name()
            if not cleaned_data.get("email_pagador"):
                cleaned_data["email_pagador"] = adesao.federado.email
        if cleaned_data.get("valor") is None:
            self.add_error("valor", "Informe o valor ou selecione uma adesão com valor contratado.")
        return cleaned_data
