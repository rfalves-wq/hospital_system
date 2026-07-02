from datetime import date

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.utils import timezone

from recepcao.models import Recepcao


class Acolhimento(models.Model):

    TIPO_ATENDIMENTO = [
        ('NORMAL', 'Atendimento Normal'),
        ('RISCO', 'Risco'),
        ('PREFERENCIAL', 'Atendimento Preferencial'),
    ]

    STATUS_CHOICES = [
        ('RECEPCAO', 'Aguardando Recepção'),
        ('CLASSIFICACAO', 'Aguardando Classificação'),
        ('CONSULTA', 'Aguardando Consulta'),
        ('FINALIZADO', 'Finalizado'),
    ]

    paciente = models.ForeignKey(
        Recepcao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acolhimentos'
    )

    nome_paciente = models.CharField(max_length=200)

    cpf = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        db_index=True
    )

    numero_bam = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        blank=True,
        null=True,
        verbose_name='Nº BAM'
    )

    data_nascimento = models.DateField()

    idade = models.PositiveIntegerField(
        blank=True,
        null=True,
        editable=False
    )

    pressao_arterial = models.CharField(
        max_length=20,
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
        blank=True,
        null=True
    )

    pulso = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    dor = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10)
        ]
    )

    tipo_atendimento = models.CharField(
        max_length=20,
        choices=TIPO_ATENDIMENTO
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RECEPCAO'
    )

    data_acolhimento = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        # Calcula automaticamente a idade
        if self.data_nascimento:
            hoje = date.today()
            self.idade = (
                hoje.year
                - self.data_nascimento.year
                - (
                    (hoje.month, hoje.day)
                    < (self.data_nascimento.month, self.data_nascimento.day)
                )
            )

        # Gera automaticamente o número BAM
        if not self.numero_bam:

            hoje = timezone.now().date()
            prefixo = hoje.strftime("%Y%m%d")

            with transaction.atomic():

                ultimo = (
                    type(self).objects
                    .select_for_update()
                    .filter(numero_bam__startswith=prefixo)
                    .order_by('-numero_bam')
                    .first()
                )

                if ultimo and ultimo.numero_bam:
                    sequencial = int(ultimo.numero_bam[-4:]) + 1
                else:
                    sequencial = 1

                self.numero_bam = f"{prefixo}{sequencial:04d}"

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-data_acolhimento']
        verbose_name = 'Acolhimento'
        verbose_name_plural = 'Acolhimentos'

    def __str__(self):
        return f"{self.nome_paciente} - {self.get_tipo_atendimento_display()}"