from datetime import timedelta

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from acolhimento.models import Acolhimento


class ManifestacaoOuvidoria(models.Model):
    RECLAMACAO = "RECLAMACAO"
    ELOGIO = "ELOGIO"
    SUGESTAO = "SUGESTAO"
    DENUNCIA = "DENUNCIA"
    INFORMACAO = "INFORMACAO"
    OCORRENCIA = "OCORRENCIA"
    OUTRO = "OUTRO"

    TIPO_CHOICES = [
        (RECLAMACAO, "Reclamacao"),
        (ELOGIO, "Elogio"),
        (SUGESTAO, "Sugestao"),
        (DENUNCIA, "Denuncia"),
        (INFORMACAO, "Pedido de informacao"),
        (OCORRENCIA, "Ocorrencia"),
        (OUTRO, "Outro"),
    ]

    PRESENCIAL = "PRESENCIAL"
    TELEFONE = "TELEFONE"
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"
    FORMULARIO = "FORMULARIO"
    CANAL_OUTRO = "OUTRO"

    CANAL_CHOICES = [
        (PRESENCIAL, "Presencial"),
        (TELEFONE, "Telefone"),
        (WHATSAPP, "WhatsApp"),
        (EMAIL, "E-mail"),
        (FORMULARIO, "Formulario"),
        (CANAL_OUTRO, "Outro"),
    ]

    BAIXA = "BAIXA"
    NORMAL = "NORMAL"
    URGENTE = "URGENTE"
    CRITICA = "CRITICA"

    PRIORIDADE_CHOICES = [
        (BAIXA, "Baixa"),
        (NORMAL, "Normal"),
        (URGENTE, "Urgente"),
        (CRITICA, "Critica"),
    ]

    ABERTA = "ABERTA"
    EM_ANALISE = "EM_ANALISE"
    AGUARDANDO_SETOR = "AGUARDANDO_SETOR"
    RESPONDIDA = "RESPONDIDA"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"

    STATUS_CHOICES = [
        (ABERTA, "Aberta"),
        (EM_ANALISE, "Em analise"),
        (AGUARDANDO_SETOR, "Aguardando setor"),
        (RESPONDIDA, "Respondida"),
        (CONCLUIDA, "Concluida"),
        (CANCELADA, "Cancelada"),
    ]
    STATUS_ATIVOS = (ABERTA, EM_ANALISE, AGUARDANDO_SETOR)

    SETOR_CHOICES = [
        ("", "---------"),
        ("Acolhimento", "Acolhimento"),
        ("Recepcao", "Recepcao"),
        ("Classificacao", "Classificacao"),
        ("Medico", "Medico"),
        ("Medicacao", "Medicacao"),
        ("Farmacia", "Farmacia"),
        ("Laboratorio", "Laboratorio"),
        ("Imagem", "Imagem"),
        ("Internacao", "Internacao"),
        ("Ambulancia", "Ambulancia"),
        ("Almoxarifado", "Almoxarifado"),
        ("Administrativo", "Administrativo"),
        ("TI", "TI"),
        ("Outro", "Outro"),
    ]

    protocolo = models.CharField(max_length=24, unique=True, db_index=True, blank=True, default="")
    acolhimento = models.ForeignKey(
        Acolhimento,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="manifestacoes_ouvidoria",
    )
    numero_bam = models.CharField(max_length=20, blank=True, default="", db_index=True)
    nome_manifestante = models.CharField(max_length=180)
    cpf_manifestante = models.CharField(max_length=14, blank=True, default="", db_index=True)
    telefone = models.CharField(max_length=30, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    paciente_nome = models.CharField(max_length=180, blank=True, default="")

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=RECLAMACAO, db_index=True)
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES, default=PRESENCIAL)
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default=NORMAL, db_index=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=ABERTA, db_index=True)
    setor_envolvido = models.CharField(
        max_length=80,
        choices=SETOR_CHOICES,
        blank=True,
        default="",
        db_index=True,
    )

    titulo = models.CharField(max_length=180)
    relato = models.TextField()
    providencias = models.TextField(blank=True, default="")
    resposta = models.TextField(blank=True, default="")
    observacoes_internas = models.TextField(blank=True, default="")

    responsavel_nome = models.CharField(max_length=150, blank=True, default="")
    responsavel_registro = models.CharField(max_length=60, blank=True, default="")
    prazo_resposta = models.DateField(blank=True, null=True, db_index=True)

    aberto_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="manifestacoes_ouvidoria_abertas",
    )
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    respondido_em = models.DateTimeField(blank=True, null=True)
    concluido_em = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Manifestacao de ouvidoria"
        verbose_name_plural = "Manifestacoes de ouvidoria"
        indexes = [
            models.Index(fields=["status", "prioridade", "criado_em"], name="ouv_status_prio_dt_idx"),
            models.Index(fields=["setor_envolvido", "status"], name="ouv_setor_status_idx"),
            models.Index(fields=["prazo_resposta", "status"], name="ouv_prazo_status_idx"),
            models.Index(fields=["tipo", "criado_em"], name="ouv_tipo_dt_idx"),
        ]

    def __str__(self):
        return f"{self.protocolo} - {self.nome_manifestante}"

    def gerar_protocolo(self):
        hoje = timezone.now().date()
        prefixo = hoje.strftime("SAC%Y%m%d")

        with transaction.atomic():
            ultimo = (
                type(self).objects
                .select_for_update()
                .filter(protocolo__startswith=prefixo)
                .order_by("-protocolo")
                .first()
            )
            sequencial = int(ultimo.protocolo[-4:]) + 1 if ultimo and ultimo.protocolo else 1

        return f"{prefixo}{sequencial:04d}"

    def preencher_do_acolhimento(self):
        if not self.acolhimento:
            return

        self.numero_bam = self.numero_bam or self.acolhimento.numero_bam or ""
        self.paciente_nome = self.paciente_nome or self.acolhimento.nome_paciente or ""
        self.cpf_manifestante = self.cpf_manifestante or self.acolhimento.cpf or ""

    def definir_prazo_padrao(self):
        if self.prazo_resposta:
            return

        dias = 2 if self.prioridade in [self.URGENTE, self.CRITICA] else 7
        self.prazo_resposta = timezone.now().date() + timedelta(days=dias)

    def save(self, *args, **kwargs):
        if not self.protocolo:
            self.protocolo = self.gerar_protocolo()

        self.preencher_do_acolhimento()
        self.definir_prazo_padrao()

        if self.status == self.RESPONDIDA and not self.respondido_em:
            self.respondido_em = timezone.now()
        if self.status == self.CONCLUIDA and not self.concluido_em:
            self.concluido_em = timezone.now()

        super().save(*args, **kwargs)

    @property
    def em_aberto(self):
        return self.status in self.STATUS_ATIVOS

    @property
    def prazo_vencido(self):
        return self.em_aberto and self.prazo_resposta and self.prazo_resposta < timezone.now().date()

    @property
    def vence_hoje(self):
        return self.em_aberto and self.prazo_resposta == timezone.now().date()

    @property
    def dias_prazo(self):
        if not self.prazo_resposta:
            return None

        return (self.prazo_resposta - timezone.now().date()).days


class AndamentoOuvidoria(models.Model):
    manifestacao = models.ForeignKey(
        ManifestacaoOuvidoria,
        on_delete=models.CASCADE,
        related_name="andamentos",
    )
    status = models.CharField(
        max_length=30,
        choices=ManifestacaoOuvidoria.STATUS_CHOICES,
        blank=True,
        default="",
    )
    anotacao = models.TextField()
    profissional_nome = models.CharField(max_length=150, blank=True, default="")
    profissional_registro = models.CharField(max_length=60, blank=True, default="")
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="andamentos_ouvidoria",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Andamento de ouvidoria"
        verbose_name_plural = "Andamentos de ouvidoria"
        indexes = [
            models.Index(fields=["manifestacao", "criado_em"], name="ouv_and_manif_dt_idx"),
        ]

    def __str__(self):
        return f"{self.manifestacao.protocolo} - {self.criado_em:%d/%m/%Y %H:%M}"
