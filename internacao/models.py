from django.db import models
from django.utils import timezone

from acolhimento.models import Acolhimento
from cadastros.models import normalizar_codigo


class SetorInternacao(models.Model):
    codigo = models.CharField(max_length=40, unique=True, db_index=True)
    nome = models.CharField(max_length=120, unique=True)
    ativo = models.BooleanField(default=True, db_index=True)
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "nome"]
        verbose_name = "Setor de internacao"
        verbose_name_plural = "Setores de internacao"

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = normalizar_codigo(self.nome, tamanho=40)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class LeitoInternacao(models.Model):
    ATIVO = "ATIVO"
    MANUTENCAO = "MANUTENCAO"
    BLOQUEADO = "BLOQUEADO"

    STATUS_OPERACIONAL_CHOICES = [
        (ATIVO, "Ativo"),
        (MANUTENCAO, "Em manutencao"),
        (BLOQUEADO, "Bloqueado"),
    ]

    CLINICO = "CLINICO"
    OBSERVACAO = "OBSERVACAO"
    ISOLAMENTO = "ISOLAMENTO"
    UTI = "UTI"
    OUTRO = "OUTRO"

    TIPO_CHOICES = [
        (CLINICO, "Clinico"),
        (OBSERVACAO, "Observacao"),
        (ISOLAMENTO, "Isolamento"),
        (UTI, "UTI"),
        (OUTRO, "Outro"),
    ]

    setor = models.ForeignKey(
        SetorInternacao,
        on_delete=models.PROTECT,
        related_name="leitos",
    )
    codigo = models.CharField(max_length=40, db_index=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=CLINICO)
    status_operacional = models.CharField(
        max_length=20,
        choices=STATUS_OPERACIONAL_CHOICES,
        default=ATIVO,
        db_index=True,
    )
    observacao = models.CharField(max_length=180, blank=True, default="")
    ordem = models.PositiveSmallIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["setor__ordem", "ordem", "codigo"]
        verbose_name = "Leito de internacao"
        verbose_name_plural = "Leitos de internacao"
        constraints = [
            models.UniqueConstraint(
                fields=["setor", "codigo"],
                name="leito_unico_por_setor",
            ),
        ]
        indexes = [
            models.Index(fields=["status_operacional", "codigo"], name="leito_status_codigo_idx"),
        ]

    @property
    def ativo(self):
        return self.status_operacional == self.ATIVO

    def __str__(self):
        return f"{self.codigo} - {self.setor.nome}"


class Internacao(models.Model):
    STATUS_CHOICES = [
        ("INTERNADO", "Internado"),
        ("ALTA", "Alta da Internação"),
        ("TRANSFERIDO", "Transferido"),
    ]

    acolhimento = models.OneToOneField(
        Acolhimento,
        on_delete=models.CASCADE,
        related_name="internacao",
    )
    leito_ref = models.ForeignKey(
        LeitoInternacao,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="internacoes",
        verbose_name="Leito normalizado",
    )
    leito = models.CharField(max_length=40)
    setor = models.CharField(max_length=120, blank=True, default="")
    diagnostico_admissao = models.TextField(blank=True, default="")
    cuidados = models.TextField(blank=True, default="")
    profissional_responsavel = models.CharField(max_length=150, blank=True, default="")
    profissional_responsavel_registro = models.CharField(max_length=50, blank=True, default="")
    observacoes = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="INTERNADO",
    )
    data_internacao = models.DateTimeField(default=timezone.now)
    data_alta = models.DateTimeField(blank=True, null=True)
    resumo_alta = models.TextField(blank=True, default="")
    profissional_alta = models.CharField(max_length=150, blank=True, default="")
    profissional_alta_registro = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        ordering = ["-data_internacao"]
        verbose_name = "Internação"
        verbose_name_plural = "Internações"

    def __str__(self):
        return f"{self.acolhimento.numero_bam} - Leito {self.leito}"

    def sincronizar_leito_normalizado(self):
        if self.leito_ref_id:
            self.leito = self.leito or self.leito_ref.codigo
            self.setor = self.setor or self.leito_ref.setor.nome
            return

        codigo = (self.leito or "").strip()
        if not codigo:
            return

        setor_nome = (self.setor or "Internacao").strip()
        setor, _criado = SetorInternacao.objects.get_or_create(
            nome=setor_nome,
            defaults={"codigo": normalizar_codigo(setor_nome, tamanho=40)},
        )
        self.leito_ref, _criado = LeitoInternacao.objects.get_or_create(
            setor=setor,
            codigo=codigo,
            defaults={"ordem": 999},
        )

    def save(self, *args, **kwargs):
        self.sincronizar_leito_normalizado()
        super().save(*args, **kwargs)


class EvolucaoInternacao(models.Model):
    internacao = models.ForeignKey(
        Internacao,
        on_delete=models.CASCADE,
        related_name="evolucoes",
    )
    data_evolucao = models.DateTimeField(default=timezone.now)
    pressao_arterial = models.CharField(max_length=20, blank=True, default="")
    temperatura = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
    )
    pulso = models.PositiveIntegerField(blank=True, null=True)
    frequencia_respiratoria = models.PositiveIntegerField(blank=True, null=True)
    saturacao = models.PositiveIntegerField(blank=True, null=True)
    evolucao = models.TextField()
    conduta = models.TextField(blank=True, default="")
    profissional = models.CharField(max_length=150, blank=True, default="")
    profissional_registro = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        ordering = ["-data_evolucao"]
        verbose_name = "Evolução da Internação"
        verbose_name_plural = "Evoluções da Internação"

    def __str__(self):
        return f"Evolução {self.internacao.acolhimento.numero_bam} - {self.data_evolucao:%d/%m/%Y %H:%M}"
