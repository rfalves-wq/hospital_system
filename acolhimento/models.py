from datetime import date, timedelta

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.utils import timezone

from recepcao.models import Recepcao


def hora_atual():
    return timezone.now().time()


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
    ('PROCEDIMENTOS', 'Aguardando Procedimentos'),
    ('RETORNO_MEDICO', 'Retorno ao Médico'),
    ('OBSERVACAO', 'Em Observação'),
    ('INTERNACAO', 'Internação'),
    ('AUSENTE', 'Ausente'),
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

    status_antes_ausencia = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        blank=True,
        default='',
        verbose_name='Status antes da ausÃªncia'
    )

    data_ausente = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data da ausÃªncia'
    )

    hora_chegada = models.TimeField(
        blank=True,
        null=True,
        default=hora_atual,
        verbose_name='Hora da chegada'
    )

    chamadas_classificacao = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Chamadas na classificação'
    )

    profissional_responsavel = models.CharField(
        max_length=150,
        blank=True,
        default='',
        verbose_name='Profissional responsavel'
    )

    profissional_responsavel_conselho = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='Conselho profissional'
    )

    profissional_responsavel_registro = models.CharField(
        max_length=40,
        blank=True,
        default='',
        verbose_name='Registro profissional'
    )

    medico_atendimento_nome = models.CharField(
        max_length=150,
        blank=True,
        default='',
        verbose_name='Medico em atendimento'
    )

    medico_atendimento_crm = models.CharField(
        max_length=60,
        blank=True,
        default='',
        verbose_name='CRM do medico em atendimento'
    )

    medico_atendimento_consultorio = models.CharField(
        max_length=80,
        blank=True,
        default='',
        verbose_name='Consultorio do atendimento medico'
    )

    medico_atendimento_inicio = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Inicio do atendimento medico'
    )

    data_ultima_chamada_classificacao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Última chamada na classificação'
    )

    ausente_classificacao = models.BooleanField(
        default=False,
        verbose_name='Ausente na classificação'
    )

    data_ausente_classificacao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data da ausência na classificação'
    )

    data_acolhimento = models.DateTimeField(
        auto_now_add=True
    )

    def reenviar_para_recepcao(self):
        self.status = 'RECEPCAO'
        self.status_antes_ausencia = ''
        self.data_ausente = None
        self.save(update_fields=['status', 'status_antes_ausencia', 'data_ausente'])

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        monitora_status = update_fields is None or "status" in update_fields
        status_anterior = None

        if self.pk and monitora_status:
            try:
                status_anterior = type(self).objects.only("status").get(pk=self.pk).status
            except type(self).DoesNotExist:
                status_anterior = None

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

        if not self.hora_chegada:
            self.hora_chegada = hora_atual()

        super().save(*args, **kwargs)

        if monitora_status:
            from .tempos import sincronizar_permanencia_status

            sincronizar_permanencia_status(self, status_anterior)

    class Meta:
        ordering = ['-data_acolhimento']
        verbose_name = 'Acolhimento'
        verbose_name_plural = 'Acolhimentos'
        indexes = [
            models.Index(fields=['status', 'data_acolhimento'], name='acolh_status_data_idx'),
            models.Index(fields=['data_acolhimento'], name='acolh_data_idx'),
            models.Index(fields=['status', 'data_ausente'], name='acolh_status_aus_idx'),
            models.Index(
                fields=['ausente_classificacao', 'data_ausente_classificacao'],
                name='acolh_aus_class_idx',
            ),
        ]

    def __str__(self):
        return f"{self.nome_paciente} - {self.get_tipo_atendimento_display()}"


class PermanenciaSetorAtendimento(models.Model):
    SETOR_CHOICES = [
        ("ACOLHIMENTO", "Acolhimento"),
        ("RECEPCAO", "Recepcao"),
        ("CLASSIFICACAO", "Classificacao de risco"),
        ("MEDICO", "Medico"),
        ("PROCEDIMENTOS", "Procedimentos"),
        ("FARMACIA", "Farmacia"),
        ("MEDICACAO", "Medicacao"),
        ("LABORATORIO", "Laboratorio"),
        ("IMAGEM", "Imagem"),
        ("OBSERVACAO", "Observacao"),
        ("INTERNACAO", "Internacao"),
        ("AUSENTE", "Ausente"),
    ]

    ORIGEM_CHOICES = [
        ("STATUS", "Status do atendimento"),
        ("PROCEDIMENTO", "Procedimento"),
    ]

    acolhimento = models.ForeignKey(
        Acolhimento,
        on_delete=models.CASCADE,
        related_name="tempos_setores",
    )
    setor = models.CharField(max_length=30, choices=SETOR_CHOICES)
    status_origem = models.CharField(max_length=20, blank=True, default="")
    origem = models.CharField(
        max_length=20,
        choices=ORIGEM_CHOICES,
        default="STATUS",
    )
    entrada = models.DateTimeField()
    saida = models.DateTimeField(blank=True, null=True)
    observacao = models.CharField(max_length=255, blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["entrada", "id"]
        verbose_name = "Permanencia por setor"
        verbose_name_plural = "Permanencias por setor"
        indexes = [
            models.Index(fields=["acolhimento", "setor", "saida"], name="perm_setor_aberto_idx"),
            models.Index(fields=["acolhimento", "entrada"], name="perm_acolh_entrada_idx"),
        ]

    @property
    def saida_calculo(self):
        return self.saida or timezone.now()

    @property
    def duracao(self):
        if not self.entrada:
            return timedelta()

        fim = self.saida_calculo

        if fim < self.entrada:
            return timedelta()

        return fim - self.entrada

    @property
    def duracao_formatada(self):
        from .tempos import formatar_duracao

        return formatar_duracao(self.duracao)

    @property
    def em_aberto(self):
        return self.saida is None

    def __str__(self):
        return f"{self.acolhimento.numero_bam or self.acolhimento_id} - {self.get_setor_display()}"
