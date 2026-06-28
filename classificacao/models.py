from django.db import models
from acolhimento.models import Acolhimento


class ClassificacaoRisco(models.Model):

    COR_CHOICES = [
        ("VERMELHO", "Vermelho - Emergência"),
        ("LARANJA", "Laranja - Muito Urgente"),
        ("AMARELO", "Amarelo - Urgente"),
        ("VERDE", "Verde - Pouco Urgente"),
        ("AZUL", "Azul - Não Urgente"),
    ]

    acolhimento = models.OneToOneField(
        Acolhimento,
        on_delete=models.CASCADE,
        related_name="classificacao"
    )

    cor = models.CharField(max_length=20, choices=COR_CHOICES)

    queixa_principal = models.TextField()

    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )

    altura = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True
    )

    glicemia = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    saturacao = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    observacoes = models.TextField(
        blank=True
    )

    data_classificacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.acolhimento.nome_paciente} - {self.cor}"