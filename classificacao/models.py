from datetime import date

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from acolhimento.models import Acolhimento


def hora_atual():
    return timezone.now().time().replace(microsecond=0)


class ClassificacaoRisco(models.Model):

    COR_CHOICES = [
        ("VERMELHO", "Vermelho - Emergência"),
        ("LARANJA", "Laranja - Muito Urgente"),
        ("AMARELO", "Amarelo - Urgente"),
        ("VERDE", "Verde - Pouco Urgente"),
        ("AZUL", "Azul - Não Urgente"),
    ]

    FORMA_CHEGADA_CHOICES = [
    ("ESPONTANEA", "Espontânea"),
    ("SAMU", "SAMU"),
    ("AMBULANCIA", "Ambulância"),
    ("BOMBEIROS", "Corpo de Bombeiros"),
    ("TRANSFERENCIA", "Transferência"),

    ("POLICIA_MILITAR", "Polícia Militar"),
    ("POLICIA_CIVIL", "Polícia Civil"),
    ("POLICIA_FEDERAL", "Polícia Federal"),
    ("POLICIA_RODOVIARIA_FEDERAL", "Polícia Rodoviária Federal"),
    ("POLICIA_PENAL", "Polícia Penal"),
    ("POLICIA_CIENTIFICA", "Polícia Científica / Técnica"),
    ("GUARDA_MUNICIPAL", "Guarda Municipal"),
    ("FORCA_NACIONAL", "Força Nacional"),

    ("EXERCITO", "Exército Brasileiro"),
    ("MARINHA", "Marinha do Brasil"),
    ("AERONAUTICA", "Força Aérea Brasileira"),

    ("OUTROS", "Outros"),
]

    GRAVIDEZ_CHOICES = [
        ("NAO_SE_APLICA", "Não se aplica"),
        ("NAO", "Não"),
        ("SIM", "Sim"),
        ("IGNORADO", "Ignorado"),
    ]

    acolhimento = models.OneToOneField(
        Acolhimento,
        on_delete=models.CASCADE,
        related_name="classificacao"
    )

    data_chegada = models.DateField(default=date.today)
    hora_chegada = models.TimeField(default=hora_atual)

    forma_chegada = models.CharField(
        max_length=30,
        choices=FORMA_CHEGADA_CHOICES,
        default="ESPONTANEA"
    )

    usuario_responsavel = models.CharField(
        max_length=150,
        default="Sistema"
    )

    queixa_principal = models.TextField("Descrição do sintoma")

    tempo_inicio_sintoma = models.CharField(
        max_length=100,
        default="Não informado"
    )

    escala_dor = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ]
    )

    doenca_pre_existente = models.TextField(blank=True)
    alergia = models.TextField(blank=True)
    uso_medicamento = models.TextField(blank=True)

    possivel_gravidez = models.CharField(
        max_length=20,
        choices=GRAVIDEZ_CHOICES,
        blank=True,
        null=True
    )

    deficiencia = models.CharField(
        max_length=200,
        blank=True
    )

    cor = models.CharField(
        max_length=20,
        choices=COR_CHOICES
    )


    glicemia = models.PositiveIntegerField(
        blank=True,
        null=True
    )

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

    observacoes = models.TextField(blank=True)

    data_classificacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Classificação de Risco"
        verbose_name_plural = "Classificações de Risco"
        ordering = ["-data_classificacao"]

        indexes = [
            models.Index(fields=["data_classificacao"], name="classif_data_idx"),
            models.Index(fields=["usuario_responsavel", "data_classificacao"], name="classif_usuario_dt_idx"),
        ]

    def __str__(self):
        return f"{self.acolhimento.nome_paciente} - {self.get_cor_display()}"
