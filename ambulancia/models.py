from datetime import date

from django.conf import settings
from django.db import models
from django.utils import timezone

from acolhimento.models import Acolhimento


class SolicitacaoAmbulancia(models.Model):
    TRANSFERENCIA = "TRANSFERENCIA"
    EXAME_EXTERNO = "EXAME_EXTERNO"
    ALTA = "ALTA"
    REMOCAO = "REMOCAO"
    OUTRO = "OUTRO"

    TIPO_CHOICES = [
        (TRANSFERENCIA, "Transferencia"),
        (EXAME_EXTERNO, "Exame externo"),
        (ALTA, "Alta com transporte"),
        (REMOCAO, "Remocao"),
        (OUTRO, "Outro"),
    ]

    BAIXA = "BAIXA"
    NORMAL = "NORMAL"
    URGENTE = "URGENTE"
    EMERGENCIA = "EMERGENCIA"

    PRIORIDADE_CHOICES = [
        (BAIXA, "Baixa"),
        (NORMAL, "Normal"),
        (URGENTE, "Urgente"),
        (EMERGENCIA, "Emergencia"),
    ]

    SOLICITADO = "SOLICITADO"
    PREPARANDO = "PREPARANDO"
    AGUARDANDO_TRANSPORTE = "AGUARDANDO_TRANSPORTE"
    SAIU = "SAIU"
    CONCLUIDO = "CONCLUIDO"
    CANCELADO = "CANCELADO"

    STATUS_CHOICES = [
        (SOLICITADO, "Solicitado"),
        (PREPARANDO, "Em preparo"),
        (AGUARDANDO_TRANSPORTE, "Aguardando transporte"),
        (SAIU, "Saiu com paciente"),
        (CONCLUIDO, "Chegou / concluido"),
        (CANCELADO, "Cancelado"),
    ]
    STATUS_ATIVOS = (SOLICITADO, PREPARANDO, AGUARDANDO_TRANSPORTE, SAIU)

    COMBUSTIVEL_CHOICES = [
        ("", "---------"),
        ("RESERVA", "Reserva"),
        ("1/4", "1/4"),
        ("1/2", "1/2"),
        ("3/4", "3/4"),
        ("CHEIO", "Cheio"),
    ]

    acolhimento = models.ForeignKey(
        Acolhimento,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="solicitacoes_ambulancia",
    )
    numero_bam = models.CharField(max_length=20, blank=True, default="", db_index=True)
    nome_paciente = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, blank=True, default="", db_index=True)
    data_nascimento = models.DateField(blank=True, null=True)
    idade = models.PositiveIntegerField(blank=True, null=True)

    tipo_transporte = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        default=TRANSFERENCIA,
    )
    prioridade = models.CharField(
        max_length=20,
        choices=PRIORIDADE_CHOICES,
        default=NORMAL,
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=SOLICITADO,
        db_index=True,
    )

    origem = models.CharField(max_length=160, default="Hospital", blank=True)
    destino = models.CharField(max_length=220)
    unidade_destino = models.CharField(max_length=180, blank=True, default="")
    motivo = models.TextField()
    resumo_clinico = models.TextField(blank=True, default="")
    observacoes = models.TextField(blank=True, default="")

    necessita_maca = models.BooleanField(default=True)
    necessita_oxigenio = models.BooleanField(default=False)
    necessita_isolamento = models.BooleanField(default=False)
    acompanhante = models.BooleanField(default=False)

    profissional_solicitante = models.CharField(max_length=150, blank=True, default="")
    conselho_solicitante = models.CharField(max_length=20, blank=True, default="")
    registro_solicitante = models.CharField(max_length=60, blank=True, default="")
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="solicitacoes_ambulancia",
    )
    setor_solicitante = models.CharField(max_length=120, blank=True, default="")
    contato = models.CharField(max_length=120, blank=True, default="")

    responsavel_transporte = models.CharField(max_length=150, blank=True, default="")
    veiculo = models.CharField(max_length=120, blank=True, default="")
    placa = models.CharField(max_length=20, blank=True, default="")
    motorista = models.CharField(max_length=150, blank=True, default="")
    medico_transporte = models.CharField(max_length=150, blank=True, default="")
    enfermeiro_transporte = models.CharField(max_length=150, blank=True, default="")
    tecnico_transporte = models.CharField(max_length=150, blank=True, default="")
    equipamentos_medicos = models.TextField(blank=True, default="")
    checklist_saida = models.TextField(blank=True, default="")
    condicao_paciente_saida = models.TextField(blank=True, default="")
    condicao_paciente_chegada = models.TextField(blank=True, default="")
    ocorrencias_transporte = models.TextField(blank=True, default="")
    recebedor_destino = models.CharField(max_length=150, blank=True, default="")
    km_saida = models.PositiveIntegerField(blank=True, null=True)
    km_chegada = models.PositiveIntegerField(blank=True, null=True)
    combustivel_saida = models.CharField(
        max_length=20,
        choices=COMBUSTIVEL_CHOICES,
        blank=True,
        default="",
    )
    combustivel_chegada = models.CharField(
        max_length=20,
        choices=COMBUSTIVEL_CHOICES,
        blank=True,
        default="",
    )

    solicitado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    preparo_em = models.DateTimeField(blank=True, null=True)
    aguardando_transporte_em = models.DateTimeField(blank=True, null=True)
    saida_em = models.DateTimeField(blank=True, null=True)
    concluido_em = models.DateTimeField(blank=True, null=True)
    cancelado_em = models.DateTimeField(blank=True, null=True)
    status_atualizado_por = models.CharField(max_length=150, blank=True, default="")

    class Meta:
        verbose_name = "Solicitacao de ambulancia"
        verbose_name_plural = "Solicitacoes de ambulancia"
        ordering = ["-solicitado_em"]
        indexes = [
            models.Index(fields=["status", "solicitado_em"], name="amb_status_dt_idx"),
            models.Index(fields=["numero_bam", "solicitado_em"], name="amb_bam_dt_idx"),
            models.Index(fields=["prioridade", "status"], name="amb_prior_status_idx"),
        ]

    def __str__(self):
        return f"{self.nome_paciente} - {self.get_tipo_transporte_display()}"

    def preencher_paciente_do_acolhimento(self):
        if not self.acolhimento:
            return

        self.numero_bam = self.acolhimento.numero_bam or self.numero_bam
        self.nome_paciente = self.acolhimento.nome_paciente or self.nome_paciente
        self.cpf = self.acolhimento.cpf or self.cpf
        self.data_nascimento = self.acolhimento.data_nascimento or self.data_nascimento
        self.idade = self.acolhimento.idade or self.idade

    def calcular_idade(self):
        if not self.data_nascimento:
            return None

        hoje = date.today()
        return (
            hoje.year
            - self.data_nascimento.year
            - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        )

    def save(self, *args, **kwargs):
        self.preencher_paciente_do_acolhimento()

        if self.data_nascimento and self.idade is None:
            self.idade = self.calcular_idade()

        super().save(*args, **kwargs)

    def marcar_status(self, novo_status, profissional=""):
        agora = timezone.now()
        self.status = novo_status
        self.status_atualizado_por = profissional or ""

        if novo_status == self.PREPARANDO and not self.preparo_em:
            self.preparo_em = agora
        elif novo_status == self.AGUARDANDO_TRANSPORTE and not self.aguardando_transporte_em:
            self.aguardando_transporte_em = agora
        elif novo_status == self.SAIU and not self.saida_em:
            self.saida_em = agora
        elif novo_status == self.CONCLUIDO and not self.concluido_em:
            self.concluido_em = agora
        elif novo_status == self.CANCELADO and not self.cancelado_em:
            self.cancelado_em = agora

    @property
    def em_aberto(self):
        return self.status in self.STATUS_ATIVOS

    @property
    def idade_texto(self):
        if self.idade is None:
            return "-"

        return f"{self.idade} anos"

    @property
    def km_percorrido(self):
        if self.km_saida is None or self.km_chegada is None:
            return None

        if self.km_chegada < self.km_saida:
            return None

        return self.km_chegada - self.km_saida
