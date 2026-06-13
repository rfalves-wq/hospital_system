from django.db import models


class Acolhimento(models.Model):

    TIPO_ATENDIMENTO = [
        ('NORMAL', 'Atendimento Normal'),
        ('RISCO', 'Risco'),
        ('PREFERENCIAL', 'Atendimento Preferencial'),
    ]

    nome_paciente = models.CharField(
        max_length=200
    )

    cpf = models.CharField(
        max_length=14,
        blank=True,
        null=True
    )

    data_nascimento = models.DateField()

    idade = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    # Sinais Vitais

    pressao_arterial = models.CharField(
        max_length=20,
        verbose_name='PA',
        blank=True,
        null=True
    )

    temperatura = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True
    )

    frequencia_respiratoria = models.PositiveIntegerField(
        verbose_name='FR',
        blank=True,
        null=True
    )

    pulso = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    dor = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    tipo_atendimento = models.CharField(
        max_length=20,
        choices=TIPO_ATENDIMENTO
    )

    data_acolhimento = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.nome_paciente} - {self.tipo_atendimento}'

    class Meta:
        verbose_name = 'Acolhimento'
        verbose_name_plural = 'Acolhimentos'
        ordering = ['-data_acolhimento']