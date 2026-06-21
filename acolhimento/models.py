from django.db import models
from django.utils import timezone


class Acolhimento(models.Model):

    TIPO_ATENDIMENTO = [
        ('NORMAL', 'Atendimento Normal'),
        ('RISCO', 'Risco'),
        ('PREFERENCIAL', 'Atendimento Preferencial'),
    ]

    nome_paciente = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, blank=True, null=True)

    numero_bam = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Nº BAM'
    )

    data_nascimento = models.DateField()
    idade = models.PositiveIntegerField(blank=True, null=True)

    pressao_arterial = models.CharField(max_length=20, blank=True, null=True)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    frequencia_respiratoria = models.PositiveIntegerField(blank=True, null=True)
    pulso = models.PositiveIntegerField(blank=True, null=True)
    dor = models.PositiveIntegerField(blank=True, null=True)

    tipo_atendimento = models.CharField(max_length=20, choices=TIPO_ATENDIMENTO)

    data_acolhimento = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if not self.numero_bam:

            hoje = timezone.now().date()

            ultimo = (
                Acolhimento.objects
                .order_by('-id')
                .values_list('numero_bam', flat=True)
                .first()
            )

            if ultimo:
                try:
                    sequencial = int(ultimo[-4:]) + 1
                except:
                    sequencial = 1
            else:
                sequencial = 1

            self.numero_bam = f"{hoje.strftime('%Y%m%d')}{sequencial:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome_paciente} - {self.tipo_atendimento}"