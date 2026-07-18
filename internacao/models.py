from django.db import models
from django.utils import timezone

from acolhimento.models import Acolhimento


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
