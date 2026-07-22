from datetime import date

from django.db import models


class MaterialAlmoxarifado(models.Model):
    MATERIAL_HOSPITALAR = "MATERIAL_HOSPITALAR"
    EPI = "EPI"
    HIGIENE_LIMPEZA = "HIGIENE_LIMPEZA"
    ESCRITORIO = "ESCRITORIO"
    MANUTENCAO = "MANUTENCAO"
    NUTRICAO = "NUTRICAO"
    ROUPARIA = "ROUPARIA"
    OUTRO = "OUTRO"

    CATEGORIA_CHOICES = [
        (MATERIAL_HOSPITALAR, "Material hospitalar"),
        (EPI, "EPI"),
        (HIGIENE_LIMPEZA, "Higiene e limpeza"),
        (ESCRITORIO, "Escritorio"),
        (MANUTENCAO, "Manutencao"),
        (NUTRICAO, "Nutricao"),
        (ROUPARIA, "Rouparia"),
        (OUTRO, "Outro"),
    ]

    codigo = models.CharField(max_length=40, blank=True, default="", db_index=True)
    nome = models.CharField(max_length=180, db_index=True)
    categoria = models.CharField(
        max_length=40,
        choices=CATEGORIA_CHOICES,
        default=MATERIAL_HOSPITALAR,
        db_index=True,
    )
    descricao = models.CharField(max_length=220, blank=True, default="")
    marca = models.CharField(max_length=120, blank=True, default="")
    unidade_medida = models.CharField(max_length=50, blank=True, default="unidade")
    fornecedor = models.CharField(max_length=180, blank=True, default="")
    localizacao = models.CharField(max_length=120, blank=True, default="")
    estoque_atual = models.PositiveIntegerField(default=0)
    estoque_minimo = models.PositiveIntegerField(default=0)
    lote_atual = models.CharField(max_length=120, blank=True, default="")
    validade = models.DateField(blank=True, null=True)
    ativo = models.BooleanField(default=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["categoria", "nome", "marca"]
        verbose_name = "Material do almoxarifado"
        verbose_name_plural = "Materiais do almoxarifado"
        indexes = [
            models.Index(fields=["ativo", "categoria", "nome"], name="almox_mat_cat_nome_idx"),
            models.Index(fields=["ativo", "validade"], name="almox_mat_valid_idx"),
            models.Index(fields=["codigo", "ativo"], name="almox_mat_cod_idx"),
        ]

    def __str__(self):
        partes = [self.nome]

        if self.marca:
            partes.append(self.marca)

        if self.descricao:
            partes.append(self.descricao)

        return " - ".join(partes)

    @property
    def descricao_completa(self):
        return str(self)

    @property
    def estoque_baixo(self):
        return self.ativo and self.estoque_atual <= self.estoque_minimo

    @property
    def zerado(self):
        return self.ativo and self.estoque_atual <= 0

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
    def texto_validade(self):
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


class MovimentacaoAlmoxarifado(models.Model):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    AJUSTE = "AJUSTE"

    TIPO_CHOICES = [
        (ENTRADA, "Entrada"),
        (SAIDA, "Saida"),
        (AJUSTE, "Ajuste"),
    ]

    SETOR_CHOICES = [
        ("", "---------"),
        ("Acolhimento", "Acolhimento"),
        ("Recepcao", "Recepcao"),
        ("Classificacao", "Classificacao"),
        ("Medico", "Medico"),
        ("Medicacao", "Medicacao"),
        ("Farmacia", "Farmacia"),
        ("Laboratorio", "Laboratorio"),
        ("Imagem", "Imagem"),
        ("Internacao", "Internacao"),
        ("Ambulancia", "Ambulancia"),
        ("Higienizacao", "Higienizacao"),
        ("Manutencao", "Manutencao"),
        ("Administrativo", "Administrativo"),
        ("Outro", "Outro"),
    ]

    material = models.ForeignKey(
        MaterialAlmoxarifado,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, db_index=True)
    quantidade = models.PositiveIntegerField()
    saldo_anterior = models.PositiveIntegerField(default=0)
    saldo_atual = models.PositiveIntegerField(default=0)
    lote = models.CharField(max_length=120, blank=True, default="")
    validade = models.DateField(blank=True, null=True)
    setor_destino = models.CharField(
        max_length=80,
        choices=SETOR_CHOICES,
        blank=True,
        default="",
        db_index=True,
    )
    origem_destino = models.CharField(max_length=180, blank=True, default="")
    solicitante_nome = models.CharField(max_length=150, blank=True, default="")
    profissional_nome = models.CharField(max_length=150)
    profissional_registro = models.CharField(max_length=60, blank=True, default="")
    observacao = models.TextField(blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Movimentacao do almoxarifado"
        verbose_name_plural = "Movimentacoes do almoxarifado"
        indexes = [
            models.Index(fields=["material", "criado_em"], name="almox_mov_mat_dt_idx"),
            models.Index(fields=["tipo", "criado_em"], name="almox_mov_tipo_dt_idx"),
            models.Index(fields=["setor_destino", "criado_em"], name="almox_mov_setor_dt_idx"),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.material} - {self.quantidade}"
