from django.conf import settings
from django.db import models

from acolhimento.models import Acolhimento


class ChamadaPainel(models.Model):
    CHAMADA = "CHAMADA"
    AUSENCIA = "AUSENCIA"
    RETORNO = "RETORNO"

    RECEPCAO = "RECEPCAO"
    CLASSIFICACAO = "CLASSIFICACAO"
    MEDICO = "MEDICO"
    MEDICACAO = "MEDICACAO"

    TIPO_CHOICES = [
        (CHAMADA, "Chamada"),
        (AUSENCIA, "Ausencia"),
        (RETORNO, "Retorno para fila"),
    ]

    SETOR_CHOICES = [
        (RECEPCAO, "Recepcao"),
        (CLASSIFICACAO, "Classificacao de risco"),
        (MEDICO, "Medico"),
        (MEDICACAO, "Sala de medicacao"),
    ]

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default=CHAMADA,
    )
    setor = models.CharField(max_length=30, choices=SETOR_CHOICES)
    acolhimento = models.ForeignKey(
        Acolhimento,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="chamadas_painel",
    )
    numero_bam = models.CharField(max_length=30, blank=True, default="")
    paciente_nome = models.CharField(max_length=200)
    local_destino = models.CharField(max_length=120, blank=True, default="")
    observacao = models.CharField(max_length=160, blank=True, default="")
    visivel_painel = models.BooleanField(default=True, verbose_name="Visivel no painel")
    chamado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="chamadas_painel_realizadas",
    )
    chamado_por_nome = models.CharField(max_length=120, blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Chamada do painel"
        verbose_name_plural = "Chamadas do painel"
        indexes = [
            models.Index(fields=["setor", "criado_em"], name="chamada_setor_dt_idx"),
            models.Index(fields=["acolhimento", "setor", "tipo"], name="chamada_acolh_set_idx"),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.get_setor_display()} - {self.paciente_nome}"
