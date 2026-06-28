from django.db import models, transaction
from django.utils import timezone
from recepcao.models import Recepcao

class Acolhimento(models.Model):

    TIPO_ATENDIMENTO = [
        ('NORMAL', 'Atendimento Normal'),
        ('RISCO', 'Risco'),
        ('PREFERENCIAL', 'Atendimento Preferencial'),
    ]

    nome_paciente = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    paciente = models.ForeignKey(
    Recepcao,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='acolhimentos'
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
    idade = models.PositiveIntegerField(blank=True, null=True)

    pressao_arterial = models.CharField(max_length=20, blank=True, null=True)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    frequencia_respiratoria = models.PositiveIntegerField(blank=True, null=True)
    pulso = models.PositiveIntegerField(blank=True, null=True)
    dor = models.PositiveIntegerField(blank=True, null=True)

    tipo_atendimento = models.CharField(max_length=20, choices=TIPO_ATENDIMENTO)
    STATUS_CHOICES = [
    ('RECEPCAO', 'Aguardando Recepção'),
    ('CLASSIFICACAO', 'Aguardando Classificação'),
    ('CONSULTA', 'Aguardando Consulta'),
    ('FINALIZADO', 'Finalizado'),
]

    status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default='RECEPCAO'
)
    

    data_acolhimento = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if not self.numero_bam:

            # 🔴 CORRETO: evita erro de timezone "naive datetime"
            hoje = timezone.now().date()
            prefixo = hoje.strftime("%Y%m%d")

            with transaction.atomic():

                ultimo = (
                    Acolhimento.objects
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

    def __str__(self):
        return f"{self.nome_paciente} - {self.tipo_atendimento}"