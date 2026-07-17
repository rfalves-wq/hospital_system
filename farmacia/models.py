from datetime import date

from django.db import models

from medico.models import ConsultaMedica


class MedicamentoEstoque(models.Model):
    COMPRIMIDOS = "COMPRIMIDOS"
    INJETAVEIS = "INJETAVEIS"
    FRASCO_SOLUCAO_XAROPE = "FRASCO_SOLUCAO_XAROPE"
    POMADAS_CREMES_GEL = "POMADAS_CREMES_GEL"
    PSICOTROPICOS = "PSICOTROPICOS"

    CATEGORIA_CHOICES = [
        (COMPRIMIDOS, "MEDICAMENTOS COMPRIMIDOS"),
        (INJETAVEIS, "MEDICAMENTOS INJETÁVEIS"),
        (FRASCO_SOLUCAO_XAROPE, "MEDICAMENTOS FRASCO / SOLUÇÃO E XAROPE"),
        (POMADAS_CREMES_GEL, "POMADAS / CREMES / GEL"),
        (PSICOTROPICOS, "PSICOTRÓPICOS"),
    ]

    ORAL = "ORAL"
    SUBLINGUAL = "SUBLINGUAL"
    ENDOVENOSA = "ENDOVENOSA"
    INTRAMUSCULAR = "INTRAMUSCULAR"
    SUBCUTANEA = "SUBCUTANEA"
    INALATORIA = "INALATORIA"
    TOPICA = "TOPICA"
    OFTALMICA = "OFTALMICA"
    OTOLOGICA = "OTOLOGICA"
    NASAL = "NASAL"
    RETAL = "RETAL"
    VAGINAL = "VAGINAL"
    OUTRA = "OUTRA"

    METODO_APLICACAO_CHOICES = [
        (ORAL, "Oral"),
        (SUBLINGUAL, "Sublingual"),
        (ENDOVENOSA, "Endovenosa / EV"),
        (INTRAMUSCULAR, "Intramuscular / IM"),
        (SUBCUTANEA, "Subcutanea / SC"),
        (INALATORIA, "Inalatoria"),
        (TOPICA, "Topica"),
        (OFTALMICA, "Oftalmica"),
        (OTOLOGICA, "Otologica"),
        (NASAL, "Nasal"),
        (RETAL, "Retal"),
        (VAGINAL, "Vaginal"),
        (OUTRA, "Outra"),
    ]

    nome = models.CharField(max_length=180, db_index=True)
    categoria = models.CharField(
        max_length=40,
        choices=CATEGORIA_CHOICES,
        default=COMPRIMIDOS,
        db_index=True
    )
    metodo_aplicacao = models.CharField(
        max_length=40,
        choices=METODO_APLICACAO_CHOICES,
        default=ORAL,
        db_index=True,
        verbose_name="Metodo de aplicacao"
    )
    principio_ativo = models.CharField(max_length=180, blank=True, default="")
    apresentacao = models.CharField(
        max_length=180,
        blank=True,
        default="",
        help_text="Ex: comprimido, ampola, frasco, bolsa, gotas."
    )
    concentracao = models.CharField(
        max_length=120,
        blank=True,
        default="",
        help_text="Ex: 500 mg, 1 g/2 ml, 0,9%."
    )
    unidade_medida = models.CharField(
        max_length=50,
        blank=True,
        default="unidade"
    )
    estoque_atual = models.PositiveIntegerField(default=0)
    estoque_minimo = models.PositiveIntegerField(default=0)
    lote_atual = models.CharField(max_length=120, blank=True, default="")
    validade = models.DateField(blank=True, null=True)
    localizacao = models.CharField(
        max_length=120,
        blank=True,
        default="",
        help_text="Ex: armário, prateleira ou geladeira."
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["categoria", "nome", "apresentacao", "concentracao"]
        verbose_name = "Medicamento em Estoque"
        verbose_name_plural = "Medicamentos em Estoque"
        indexes = [
            models.Index(fields=["ativo", "categoria", "nome"], name="med_ativo_cat_nome_idx"),
            models.Index(fields=["ativo", "validade"], name="med_ativo_valid_idx"),
            models.Index(fields=["categoria", "metodo_aplicacao"], name="med_cat_metodo_idx"),
        ]

    def __str__(self):
        partes = [self.nome]

        if self.concentracao:
            partes.append(self.concentracao)

        if self.apresentacao:
            partes.append(self.apresentacao)

        return " - ".join(partes)

    @property
    def descricao_completa(self):
        return str(self)

    @property
    def estoque_baixo(self):
        return self.ativo and self.estoque_atual <= self.estoque_minimo

    @property
    def disponivel_para_prescricao(self):
        return self.ativo and self.estoque_atual > 0

    @property
    def dias_para_vencer(self):
        if not self.validade:
            return None

        return (self.validade - date.today()).days

    @property
    def classe_validade(self):
        dias = self.dias_para_vencer

        if dias is None:
            return "sem-validade"

        if dias < 0:
            return "vencido"

        if dias <= 30:
            return "vence-logo"

        return "em-dia"

    @property
    def texto_dias_validade(self):
        dias = self.dias_para_vencer

        if dias is None:
            return "Sem validade"

        if dias < 0:
            return f"Vencido ha {abs(dias)} dia(s)"

        if dias == 0:
            return "Vence hoje"

        if dias == 1:
            return "Falta 1 dia"

        return f"Faltam {dias} dias"


class MovimentacaoEstoque(models.Model):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    AJUSTE = "AJUSTE"

    TIPO_CHOICES = [
        (ENTRADA, "Entrada"),
        (SAIDA, "Saída"),
        (AJUSTE, "Ajuste"),
    ]

    medicamento = models.ForeignKey(
        MedicamentoEstoque,
        on_delete=models.PROTECT,
        related_name="movimentacoes"
    )
    consulta = models.ForeignKey(
        ConsultaMedica,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="movimentacoes_farmacia"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES
    )
    quantidade = models.PositiveIntegerField()
    saldo_anterior = models.PositiveIntegerField(default=0)
    saldo_atual = models.PositiveIntegerField(default=0)
    lote = models.CharField(max_length=120, blank=True, default="")
    validade = models.DateField(blank=True, null=True)
    origem_destino = models.CharField(
        max_length=180,
        blank=True,
        default="",
        help_text="Ex: fornecedor, setor, paciente, perda ou inventário."
    )
    profissional_nome = models.CharField(max_length=150)
    profissional_registro = models.CharField(max_length=60, blank=True, default="")
    observacao = models.TextField(blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"

        indexes = [
            models.Index(fields=["medicamento", "criado_em"], name="mov_med_data_idx"),
            models.Index(fields=["tipo", "criado_em"], name="mov_tipo_data_idx"),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.medicamento} - {self.quantidade}"
