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

    solicita_medicacao = models.BooleanField(default=False)
    solicita_exames_laboratoriais = models.BooleanField(default=False)
    solicita_exames_imagem = models.BooleanField(default=False)

    medicacao_realizada = models.BooleanField(default=False)
    exames_laboratoriais_realizados = models.BooleanField(default=False)
    exames_imagem_realizados = models.BooleanField(default=False)

    exames_laboratoriais = models.TextField(blank=True, default="")
    exames_imagem = models.TextField(blank=True, default="")

    prescricao = models.TextField(blank=True, default="")
    orientacoes = models.TextField(blank=True, default="")

    data_consulta = models.DateTimeField(auto_now_add=True)

    resultado_exames_laboratoriais = models.TextField(blank=True, default="")
    data_resultado_laboratorio = models.DateTimeField(blank=True, null=True)

    tecnico_laboratorio_nome = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )

    tecnico_laboratorio_registro = models.CharField(
        max_length=50,
        blank=True,
        default=""
    )

    medicamento_utilizado = models.TextField(blank=True, default="")
    dose_medicacao = models.CharField(max_length=100, blank=True, default="")
    via_medicacao = models.CharField(max_length=100, blank=True, default="")
    horario_medicacao = models.CharField(max_length=100, blank=True, default="")
    lote_medicacao = models.CharField(max_length=100, blank=True, default="")
    quantidade_medicacao = models.CharField(max_length=100, blank=True, default="")
    materiais_utilizados_medicacao = models.TextField(blank=True, default="")

    medicacao_administrada = models.TextField(blank=True, default="")
    observacoes_medicacao = models.TextField(blank=True, default="")
    profissional_medicacao_nome = models.CharField(max_length=150, blank=True, default="")
    profissional_medicacao_registro = models.CharField(max_length=50, blank=True, default="")
    data_medicacao = models.DateTimeField(blank=True, null=True)

    resultado_exames_imagem = models.TextField(blank=True, default="")
    data_resultado_imagem = models.DateTimeField(blank=True, null=True)

    resultado_raiox = models.TextField(blank=True, default="")
    data_resultado_raiox = models.DateTimeField(blank=True, null=True)
    raiox_realizado = models.BooleanField(default=False)

    tecnico_raiox_nome = models.CharField(max_length=150, blank=True, default="")
    tecnico_raiox_registro = models.CharField(max_length=50, blank=True, default="")

    resultado_tomografia = models.TextField(blank=True, default="")
    data_resultado_tomografia = models.DateTimeField(blank=True, null=True)
    tomografia_realizada = models.BooleanField(default=False)

    tecnico_tomografia_nome = models.CharField(max_length=150, blank=True, default="")
    tecnico_tomografia_registro = models.CharField(max_length=50, blank=True, default="")

    resultado_mamografia = models.TextField(blank=True, default="")
    data_resultado_mamografia = models.DateTimeField(blank=True, null=True)
    mamografia_realizada = models.BooleanField(default=False)

    tecnico_mamografia_nome = models.CharField(max_length=150, blank=True, default="")
    tecnico_mamografia_registro = models.CharField(max_length=50, blank=True, default="")

    resultado_densitometria = models.TextField(blank=True, default="")
    data_resultado_densitometria = models.DateTimeField(blank=True, null=True)
    densitometria_realizada = models.BooleanField(default=False)

    tecnico_densitometria_nome = models.CharField(max_length=150, blank=True, default="")
    tecnico_densitometria_registro = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        ordering = ["-data_consulta"]
        verbose_name = "Consulta Médica"
        verbose_name_plural = "Consultas Médicas"

    def __str__(self):
        if self.acolhimento.paciente:
            paciente = self.acolhimento.paciente.nome_completo
        else:
            paciente = self.acolhimento.nome_paciente

        return f"{paciente} - {self.medico_responsavel}"

    def setores_imagem_solicitados(self):
        texto = (self.exames_imagem or "").upper()
        setores = []

        if "RAIO-X" in texto or "RAIO X" in texto:
            setores.append("RAIO-X")

        if "TOMOGRAFIA" in texto:
            setores.append("TOMOGRAFIA")

        if "MAMOGRAFIA" in texto:
            setores.append("MAMOGRAFIA")

        if "DENSITOMETRIA" in texto:
            setores.append("DENSITOMETRIA")

        return setores

    def todos_exames_imagem_finalizados(self):
        setores = self.setores_imagem_solicitados()

        if not setores:
            return True

        if "RAIO-X" in setores and not self.raiox_realizado:
            return False

        if "TOMOGRAFIA" in setores and not self.tomografia_realizada:
            return False

        if "MAMOGRAFIA" in setores and not self.mamografia_realizada:
            return False

        if "DENSITOMETRIA" in setores and not self.densitometria_realizada:
            return False

        return True

    def todos_procedimentos_finalizados(self):
        if self.solicita_medicacao and not self.medicacao_realizada:
            return False

        if self.solicita_exames_laboratoriais and not self.exames_laboratoriais_realizados:
            return False

        if self.solicita_exames_imagem and not self.todos_exames_imagem_finalizados():
            return False

        return True