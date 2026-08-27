from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Gateway(models.TextChoices):
    """Gateways suportados; credenciais ficam fora do banco, em segredos da infraestrutura."""

    NENHUM = "nenhum", "Ainda não definido"
    PAGBANK = "pagbank", "PagBank"
    PAGARME = "pagarme", "Pagar.me"


class AmbienteGateway(models.TextChoices):
    SANDBOX = "sandbox", "Sandbox / testes"
    PRODUCAO = "producao", "Produção"


class StatusConexaoGateway(models.TextChoices):
    NAO_TESTADO = "nao_testado", "Ainda não verificada"
    CONFIGURADO = "configurado", "Configurada"
    ERRO = "erro", "Com erro"


class GatewayConfiguracao(models.Model):
    """Configuração global do provedor; segredos ficam nas variáveis da infraestrutura."""

    chave = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)
    gateway = models.CharField(
        max_length=20,
        choices=Gateway.choices,
        default=Gateway.NENHUM,
        verbose_name="Gateway ativo",
    )
    ambiente = models.CharField(
        max_length=20,
        choices=AmbienteGateway.choices,
        default=AmbienteGateway.SANDBOX,
        verbose_name="Ambiente",
    )
    ativo = models.BooleanField(
        default=False,
        verbose_name="Integração ativa",
        help_text="Ative somente depois de configurar e homologar as credenciais no ambiente da aplicação.",
    )
    aceita_cartao = models.BooleanField(default=True, verbose_name="Aceita cartão")
    aceita_boleto = models.BooleanField(default=True, verbose_name="Aceita boleto")
    aceita_pix = models.BooleanField(default=True, verbose_name="Aceita Pix")
    webhook_url = models.URLField(
        blank=True,
        verbose_name="URL do webhook",
        help_text="Endpoint público que receberá atualizações do gateway quando a integração estiver ativa.",
    )
    status_conexao = models.CharField(
        max_length=20,
        choices=StatusConexaoGateway.choices,
        default=StatusConexaoGateway.NAO_TESTADO,
        verbose_name="Status da conexão",
    )
    ultima_verificacao_em = models.DateTimeField(blank=True, null=True, verbose_name="Última verificação")
    mensagem_conexao = models.TextField(blank=True, verbose_name="Mensagem da conexão")
    observacoes = models.TextField(blank=True, verbose_name="Observações internas")
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="configuracoes_gateway_atualizadas",
        verbose_name="Último administrador",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração de gateway"
        verbose_name_plural = "Configurações de gateway"
        ordering = ["-atualizado_em"]
        constraints = [
            models.CheckConstraint(condition=Q(chave=1), name="gateway_config_chave_unica"),
            models.CheckConstraint(
                condition=Q(ativo=False) | ~Q(gateway=Gateway.NENHUM),
                name="gateway_config_ativo_provedor",
            ),
            models.CheckConstraint(
                condition=Q(ativo=False) | Q(aceita_cartao=True) | Q(aceita_boleto=True) | Q(aceita_pix=True),
                name="gateway_config_metodo_ativo",
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.ativo and self.gateway == Gateway.NENHUM:
            raise ValidationError({"gateway": "Escolha PagBank ou Pagar.me antes de ativar a integração."})
        if self.ativo and not any((self.aceita_cartao, self.aceita_boleto, self.aceita_pix)):
            raise ValidationError("Ative pelo menos um meio de pagamento para habilitar a integração.")

    def save(self, *args, **kwargs):
        self.chave = 1
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_gateway_display()} — {self.get_ambiente_display()}"


class FormaPagamento(models.TextChoices):
    CARTAO = "cartao", "Cartão de crédito"
    BOLETO = "boleto", "Boleto bancário"
    PIX = "pix", "Pix"


class StatusAdesao(models.TextChoices):
    PENDENTE = "pendente", "Pendente de ativação"
    ATIVA = "ativa", "Ativa"
    SUSPENSA = "suspensa", "Suspensa"
    INADIMPLENTE = "inadimplente", "Inadimplente"
    CANCELADA = "cancelada", "Cancelada"
    ENCERRADA = "encerrada", "Encerrada"


class StatusCobranca(models.TextChoices):
    PENDENTE = "pendente", "Aguardando pagamento"
    PROCESSANDO = "processando", "Processando"
    PAGO = "pago", "Pago"
    VENCIDA = "vencida", "Vencida"
    FALHA = "falha", "Falha no pagamento"
    CANCELADA = "cancelada", "Cancelada"
    ESTORNADA = "estornada", "Estornada"
    CONCILIACAO_MANUAL = "conciliacao_manual", "Conciliação manual"


class StatusPagamento(models.TextChoices):
    PENDENTE = "pendente", "Pendente"
    EM_ANALISE = "em_analise", "Em análise"
    AUTORIZADO = "autorizado", "Autorizado"
    PAGO = "pago", "Pago"
    FALHOU = "falhou", "Falhou"
    CANCELADO = "cancelado", "Cancelado"
    ESTORNADO = "estornado", "Estornado"


class StatusEvento(models.TextChoices):
    RECEBIDO = "recebido", "Recebido"
    PROCESSADO = "processado", "Processado"
    ERRO = "erro", "Erro no processamento"
    IGNORADO = "ignorado", "Ignorado"


class AcaoAuditoria(models.TextChoices):
    CRIACAO = "criacao", "Criação"
    ALTERACAO = "alteracao", "Alteração"
    ATIVACAO = "ativacao", "Ativação"
    SUSPENSAO = "suspensao", "Suspensão"
    CANCELAMENTO = "cancelamento", "Cancelamento"
    BAIXA_MANUAL = "baixa_manual", "Baixa manual"
    CONCILIACAO = "conciliacao", "Conciliação"
    ESTORNO = "estorno", "Estorno"
    OUTRO = "outro", "Outra ação"


class PlanoMensalidade(models.Model):
    """Plano associativo que poderá ser oferecido aos federados."""

    slug = models.SlugField(
        max_length=80,
        unique=True,
        verbose_name="Identificador interno",
        help_text="Código estável usado nas integrações e URLs internas.",
    )
    nome = models.CharField(max_length=120, verbose_name="Nome do plano")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Valor da mensalidade",
    )
    dia_vencimento = models.PositiveSmallIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(28)],
        verbose_name="Dia de vencimento",
        help_text="Use de 1 a 28 para evitar ambiguidades em fevereiro.",
    )
    gateway = models.CharField(
        max_length=20,
        choices=Gateway.choices,
        default=Gateway.NENHUM,
        verbose_name="Gateway",
    )
    gateway_plan_id = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="ID do plano no gateway",
        help_text="Preenchido somente após criação e homologação no gateway.",
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plano de mensalidade"
        verbose_name_plural = "Planos de mensalidade"
        ordering = ["nome"]
        constraints = [
            models.CheckConstraint(condition=Q(valor__gte=0), name="plano_mens_valor_nneg"),
            models.CheckConstraint(
                condition=Q(dia_vencimento__gte=1) & Q(dia_vencimento__lte=28),
                name="plano_mens_dia_1_28",
            ),
            models.UniqueConstraint(
                fields=["gateway", "gateway_plan_id"],
                condition=~Q(gateway_plan_id=""),
                name="plano_mens_gateway_id",
            ),
        ]

    def __str__(self):
        return f"{self.nome} — R$ {self.valor:.2f}"


class AdesaoMensalidade(models.Model):
    """Vínculo histórico de um federado a um plano de mensalidade."""

    federado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="adesoes_mensalidade",
        verbose_name="Federado",
    )
    plano = models.ForeignKey(
        PlanoMensalidade,
        on_delete=models.PROTECT,
        related_name="adesoes",
        verbose_name="Plano",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusAdesao.choices,
        default=StatusAdesao.PENDENTE,
        verbose_name="Situação",
    )
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FormaPagamento.choices,
        verbose_name="Forma de pagamento",
    )
    valor_contratado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Valor contratado",
        help_text="Snapshot do valor no momento da adesão.",
    )
    dia_vencimento = models.PositiveSmallIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(28)],
        verbose_name="Dia de vencimento",
    )
    data_inicio = models.DateField(default=timezone.localdate, verbose_name="Início da adesão")
    data_fim = models.DateField(blank=True, null=True, verbose_name="Fim da adesão")
    proxima_cobranca = models.DateField(blank=True, null=True, verbose_name="Próxima cobrança")
    gateway = models.CharField(
        max_length=20,
        choices=Gateway.choices,
        default=Gateway.NENHUM,
        verbose_name="Gateway utilizado",
    )
    gateway_customer_id = models.CharField(max_length=120, blank=True, verbose_name="ID do cliente no gateway")
    gateway_subscription_id = models.CharField(max_length=120, blank=True, verbose_name="ID da assinatura no gateway")
    gateway_reference = models.CharField(max_length=150, blank=True, verbose_name="Referência externa")
    observacoes = models.TextField(blank=True, verbose_name="Observações internas")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Adesão de mensalidade"
        verbose_name_plural = "Adesões de mensalidade"
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["federado", "status"], name="adesao_fed_status_idx"),
            models.Index(fields=["plano", "status"], name="adesao_plano_status_idx"),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(valor_contratado__gte=0), name="adesao_mens_valor_nneg"),
            models.CheckConstraint(
                condition=Q(dia_vencimento__gte=1) & Q(dia_vencimento__lte=28),
                name="adesao_mens_dia_1_28",
            ),
            models.CheckConstraint(
                condition=Q(data_fim__isnull=True) | Q(data_fim__gte=models.F("data_inicio")),
                name="adesao_mens_datas_validas",
            ),
            models.UniqueConstraint(
                fields=["gateway", "gateway_subscription_id"],
                condition=~Q(gateway_subscription_id=""),
                name="adesao_mens_gateway_sub",
            ),
        ]

    def __str__(self):
        nome = self.federado.get_full_name() or self.federado.get_username()
        return f"{nome} — {self.plano.nome} ({self.get_status_display()})"


class CobrancaMensalidade(models.Model):
    """Cobrança de uma competência específica da adesão."""

    adesao = models.ForeignKey(
        AdesaoMensalidade,
        on_delete=models.PROTECT,
        related_name="cobrancas",
        verbose_name="Adesão",
    )
    competencia = models.DateField(
        verbose_name="Competência",
        help_text="Use o primeiro dia do mês de referência, por exemplo 2026-08-01.",
    )
    vencimento = models.DateField(verbose_name="Vencimento")
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Valor da cobrança",
    )
    status = models.CharField(
        max_length=25,
        choices=StatusCobranca.choices,
        default=StatusCobranca.PENDENTE,
        verbose_name="Situação",
    )
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FormaPagamento.choices,
        verbose_name="Forma de pagamento",
    )
    gateway = models.CharField(max_length=20, choices=Gateway.choices, default=Gateway.NENHUM, verbose_name="Gateway")
    gateway_invoice_id = models.CharField(max_length=120, blank=True, verbose_name="ID da fatura no gateway")
    gateway_charge_id = models.CharField(max_length=120, blank=True, verbose_name="ID da cobrança no gateway")
    url_pagamento = models.URLField(blank=True, verbose_name="URL de pagamento")
    url_boleto = models.URLField(blank=True, verbose_name="URL do boleto")
    codigo_barras = models.CharField(max_length=250, blank=True, verbose_name="Código de barras")
    pix_copia_cola = models.TextField(blank=True, verbose_name="Pix copia e cola")
    pix_expira_em = models.DateTimeField(blank=True, null=True, verbose_name="Expiração do Pix")
    nome_pagador = models.CharField(max_length=255, blank=True, verbose_name="Nome do pagador na cobrança")
    documento_pagador = models.CharField(max_length=18, blank=True, verbose_name="Documento do pagador na cobrança")
    email_pagador = models.EmailField(blank=True, verbose_name="E-mail do pagador na cobrança")
    telefone_pagador = models.CharField(max_length=30, blank=True, verbose_name="Telefone do pagador na cobrança")
    pago_em = models.DateTimeField(blank=True, null=True, verbose_name="Pago em")
    ultima_sincronizacao = models.DateTimeField(blank=True, null=True, verbose_name="Última sincronização")
    observacoes = models.TextField(blank=True, verbose_name="Observações internas")
    dados_gateway = models.JSONField(default=dict, blank=True, verbose_name="Dados não sensíveis do gateway")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cobrança de mensalidade"
        verbose_name_plural = "Cobranças de mensalidade"
        ordering = ["-competencia", "-criado_em"]
        indexes = [
            models.Index(fields=["status", "vencimento"], name="cobr_status_venc_idx"),
            models.Index(fields=["adesao", "competencia"], name="cobr_adesao_comp_idx"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["adesao", "competencia"], name="cobranca_mens_competencia"),
            models.CheckConstraint(condition=Q(valor__gte=0), name="cobranca_mens_valor_nneg"),
            models.UniqueConstraint(
                fields=["gateway", "gateway_invoice_id"],
                condition=~Q(gateway_invoice_id=""),
                name="cobranca_mens_gateway_inv",
            ),
            models.UniqueConstraint(
                fields=["gateway", "gateway_charge_id"],
                condition=~Q(gateway_charge_id=""),
                name="cobranca_mens_gateway_chg",
            ),
        ]

    @property
    def esta_vencida(self):
        return self.status in {StatusCobranca.PENDENTE, StatusCobranca.PROCESSANDO} and self.vencimento < timezone.localdate()

    def __str__(self):
        return f"{self.adesao.federado.get_username()} — {self.competencia:%m/%Y} — R$ {self.valor:.2f}"


class Pagamento(models.Model):
    """Tentativa ou confirmação de pagamento de uma cobrança."""

    cobranca = models.ForeignKey(
        CobrancaMensalidade,
        on_delete=models.PROTECT,
        related_name="pagamentos",
        verbose_name="Cobrança",
    )
    tentativa = models.PositiveSmallIntegerField(default=1, verbose_name="Número da tentativa")
    gateway = models.CharField(max_length=20, choices=Gateway.choices, verbose_name="Gateway")
    forma_pagamento = models.CharField(max_length=20, choices=FormaPagamento.choices, verbose_name="Forma de pagamento")
    status = models.CharField(max_length=20, choices=StatusPagamento.choices, default=StatusPagamento.PENDENTE, verbose_name="Situação")
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Valor pago/tentado",
    )
    gateway_payment_id = models.CharField(max_length=120, blank=True, verbose_name="ID do pagamento no gateway")
    gateway_transaction_id = models.CharField(max_length=120, blank=True, verbose_name="ID da transação no gateway")
    pago_em = models.DateTimeField(blank=True, null=True, verbose_name="Confirmado em")
    falhou_em = models.DateTimeField(blank=True, null=True, verbose_name="Falhou em")
    motivo_falha = models.TextField(blank=True, verbose_name="Motivo da falha")
    dados_gateway = models.JSONField(default=dict, blank=True, verbose_name="Dados não sensíveis do gateway")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["cobranca", "status"], name="pag_cobr_status_idx"),
            models.Index(fields=["gateway", "status"], name="pag_gateway_status_idx"),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(valor__gte=0), name="pagamento_valor_nneg"),
            models.UniqueConstraint(
                fields=["gateway", "gateway_payment_id"],
                condition=~Q(gateway_payment_id=""),
                name="pag_gateway_payment_id",
            ),
        ]

    def __str__(self):
        return f"Pagamento #{self.pk or 'novo'} — {self.get_status_display()} — R$ {self.valor:.2f}"


class EventoGateway(models.Model):
    """Evento recebido do gateway para idempotência, auditoria e reprocessamento."""

    gateway = models.CharField(max_length=20, choices=Gateway.choices, verbose_name="Gateway")
    evento_id = models.CharField(max_length=160, verbose_name="ID do evento no gateway")
    tipo_evento = models.CharField(max_length=120, verbose_name="Tipo do evento")
    status = models.CharField(max_length=20, choices=StatusEvento.choices, default=StatusEvento.RECEBIDO, verbose_name="Processamento")
    assinatura_validada = models.BooleanField(default=False, verbose_name="Assinatura validada")
    payload = models.JSONField(default=dict, verbose_name="Payload recebido")
    ocorrido_em = models.DateTimeField(blank=True, null=True, verbose_name="Ocorrido em")
    recebido_em = models.DateTimeField(auto_now_add=True, verbose_name="Recebido em")
    processado_em = models.DateTimeField(blank=True, null=True, verbose_name="Processado em")
    tentativas = models.PositiveSmallIntegerField(default=0, verbose_name="Tentativas de processamento")
    erro_processamento = models.TextField(blank=True, verbose_name="Erro de processamento")
    adesao = models.ForeignKey(
        AdesaoMensalidade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_gateway",
        verbose_name="Adesão relacionada",
    )
    cobranca = models.ForeignKey(
        CobrancaMensalidade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_gateway",
        verbose_name="Cobrança relacionada",
    )

    class Meta:
        verbose_name = "Evento de gateway"
        verbose_name_plural = "Eventos de gateway"
        ordering = ["-recebido_em"]
        indexes = [
            models.Index(fields=["gateway", "status"], name="evt_gateway_status_idx"),
            models.Index(fields=["tipo_evento", "recebido_em"], name="evt_tipo_recebido_idx"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["gateway", "evento_id"], name="evento_gateway_evento_id"),
        ]

    def __str__(self):
        return f"{self.gateway} — {self.tipo_evento} — {self.evento_id}"


class AuditoriaFinanceira(models.Model):
    """Histórico das ações administrativas no domínio financeiro."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias_financeiras",
        verbose_name="Usuário responsável",
    )
    acao = models.CharField(max_length=25, choices=AcaoAuditoria.choices, verbose_name="Ação")
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, verbose_name="Tipo do objeto")
    object_id = models.PositiveBigIntegerField(verbose_name="ID do objeto")
    descricao = models.TextField(verbose_name="Descrição")
    dados_anteriores = models.JSONField(default=dict, blank=True, verbose_name="Dados anteriores")
    dados_novos = models.JSONField(default=dict, blank=True, verbose_name="Dados novos")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Auditoria financeira"
        verbose_name_plural = "Auditorias financeiras"
        ordering = ["-criado_em"]
        indexes = [
            models.Index(fields=["content_type", "object_id"], name="audit_objeto_idx"),
            models.Index(fields=["acao", "criado_em"], name="audit_acao_data_idx"),
        ]

    def __str__(self):
        return f"{self.get_acao_display()} — {self.descricao[:80]}"
