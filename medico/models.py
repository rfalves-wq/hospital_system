from django.db import models

from acolhimento.models import Acolhimento


class CID(models.Model):

    TIPO_CHOICES = [
        ("CAPITULO", "Capítulo"),
        ("GRUPO", "Grupo"),
        ("CATEGORIA", "Categoria"),
        ("SUBCATEGORIA", "Subcategoria"),
    ]

    codigo = models.CharField(max_length=20, unique=True, db_index=True)
    descricao = models.CharField(max_length=255, db_index=True)

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default="SUBCATEGORIA"
    )

    class Meta:
        ordering = ["codigo"]
        verbose_name = "CID"
        verbose_name_plural = "CIDs"

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"


class ConsultaMedica(models.Model):

    CONDUTA_CHOICES = [
        ("RETORNO", "Retorno após procedimentos"),
        ("ALTA", "Alta Médica"),
        ("OBSERVACAO", "Observação"),
        ("INTERNACAO", "Internação"),
        ("ENCAMINHAMENTO", "Encaminhamento"),
    ]

    acolhimento = models.OneToOneField(
        Acolhimento,
        on_delete=models.CASCADE,
        related_name="consulta_medica"
    )

    medico_responsavel = models.CharField(max_length=150)

    queixa_principal = models.TextField()
    historia_doenca_atual = models.TextField(blank=True, default="")
    exame_fisico = models.TextField(blank=True, default="")

    hipotese_diagnostica = models.TextField()
    cid = models.CharField(max_length=20, blank=True, default="")

    conduta = models.CharField(
        max_length=30,
        choices=CONDUTA_CHOICES
    )
    medicacao_realizada = models.BooleanField(default=False)
    exames_laboratoriais_realizados = models.BooleanField(default=False)
    exames_imagem_realizados = models.BooleanField(default=False)

    solicita_medicacao = models.BooleanField(default=False)
    solicita_exames_laboratoriais = models.BooleanField(default=False)
    solicita_exames_imagem = models.BooleanField(default=False)

    exames_laboratoriais = models.TextField(blank=True, default="")
    exames_imagem = models.TextField(blank=True, default="")

    prescricao = models.TextField(blank=True, default="")
    orientacoes = models.TextField(blank=True, default="")

    data_consulta = models.DateTimeField(auto_now_add=True)

    resultado_exames_laboratoriais = models.TextField(
    blank=True,
    default=""
)

    resultado_exames_imagem = models.TextField(
    blank=True,
    default=""
)

    data_resultado_laboratorio = models.DateTimeField(
    blank=True,
    null=True
)

    data_resultado_imagem = models.DateTimeField(
    blank=True,
    null=True
)
    
    solicita_exames_imagem = models.BooleanField(default=False)

    exames_imagem = models.TextField(
    blank=True,
    default=""
)

    exames_imagem_realizados = models.BooleanField(default=False)

    resultado_exames_imagem = models.TextField(
    blank=True,
    default=""
)

    data_resultado_imagem = models.DateTimeField(
    blank=True,
    null=True
)
    class Meta:
        ordering = ["-data_consulta"]
        verbose_name = "Consulta Médica"
        verbose_name_plural = "Consultas Médicas"

    def __str__(self):
        return f"{self.acolhimento.nome_paciente} - {self.medico_responsavel}"