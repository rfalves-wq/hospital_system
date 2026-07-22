from django.conf import settings
from django.apps import apps
from django.db import models

from accounts.models import CONSELHO_PROFISSIONAL_CHOICES
from cadastros.models import normalizar_codigo
from unidades.models import UnidadeMedica


def resolver_cadastro(model_name, valor):
    valor = (valor or "").strip()

    if not valor:
        return None

    model = apps.get_model("cadastros", model_name)
    codigo = normalizar_codigo(valor)

    return (
        model.objects.filter(codigo=codigo).first()
        or model.objects.filter(nome__iexact=valor).first()
    )


class Funcionario(models.Model):
    CLT = "CLT"
    CONTRATO = "CONTRATO"
    RPA = "RPA"
    ESTAGIO = "ESTAGIO"
    TERCEIRIZADO = "TERCEIRIZADO"
    OUTRO = "OUTRO"

    VINCULO_CHOICES = [
        ("", "---------"),
        (CLT, "CLT"),
        (CONTRATO, "Contrato"),
        (RPA, "RPA"),
        (ESTAGIO, "Estagio"),
        (TERCEIRIZADO, "Terceirizado"),
        (OUTRO, "Outro"),
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
        ("Prontuario", "Prontuario"),
        ("Ambulancia", "Ambulancia"),
        ("TI", "TI"),
        ("Administrativo", "Administrativo"),
        ("RH", "RH"),
        ("Manutencao", "Manutencao"),
        ("Almoxarifado", "Almoxarifado"),
        ("Outro", "Outro"),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="cadastro_funcionario",
    )
    nome = models.CharField(max_length=180, db_index=True)
    cpf = models.CharField(max_length=14, blank=True, default="", db_index=True)
    matricula = models.CharField(max_length=40, blank=True, default="", db_index=True)
    cargo_ref = models.ForeignKey(
        "cadastros.CargoProfissional",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="funcionarios",
        verbose_name="Cargo normalizado",
    )
    cargo = models.CharField(max_length=100, blank=True, default="", db_index=True)
    funcao_ref = models.ForeignKey(
        "cadastros.FuncaoProfissional",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="funcionarios",
        verbose_name="Funcao normalizada",
    )
    funcao = models.CharField(max_length=120, blank=True, default="")
    setor_ref = models.ForeignKey(
        "cadastros.SetorHospitalar",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="funcionarios",
        verbose_name="Setor normalizado",
    )
    setor = models.CharField(
        max_length=80,
        choices=SETOR_CHOICES,
        blank=True,
        default="",
        db_index=True,
    )
    unidade = models.ForeignKey(
        UnidadeMedica,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="funcionarios",
    )
    conselho_ref = models.ForeignKey(
        "cadastros.ConselhoProfissional",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="funcionarios",
        verbose_name="Conselho normalizado",
    )
    conselho_profissional = models.CharField(
        max_length=20,
        choices=CONSELHO_PROFISSIONAL_CHOICES,
        blank=True,
        default="",
    )
    registro_profissional = models.CharField(max_length=40, blank=True, default="")
    telefone = models.CharField(max_length=30, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    data_admissao = models.DateField(blank=True, null=True)
    data_demissao = models.DateField(blank=True, null=True)
    tipo_vinculo_ref = models.ForeignKey(
        "cadastros.TipoVinculoTrabalho",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="funcionarios",
        verbose_name="Tipo de vinculo normalizado",
    )
    tipo_vinculo = models.CharField(
        max_length=20,
        choices=VINCULO_CHOICES,
        blank=True,
        default="",
    )
    carga_horaria_semanal = models.PositiveSmallIntegerField(blank=True, null=True)
    ativo = models.BooleanField(default=True, db_index=True)
    observacoes = models.TextField(blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Funcionario"
        verbose_name_plural = "Funcionarios"
        indexes = [
            models.Index(fields=["ativo", "setor"], name="func_ativo_setor_idx"),
            models.Index(fields=["cargo", "ativo"], name="func_cargo_ativo_idx"),
        ]

    def __str__(self):
        return self.nome

    @property
    def conselho_registro(self):
        conselho = self.conselho_profissional
        if not conselho and self.conselho_ref_id:
            conselho = self.conselho_ref.codigo

        partes = [conselho, self.registro_profissional]
        return " ".join(parte for parte in partes if parte) or "-"

    @property
    def login_status(self):
        if not self.usuario:
            return "Sem login"

        return "Login ativo" if self.usuario.is_active else "Login bloqueado"

    def preencher_do_usuario(self):
        if not self.usuario:
            return

        nome_usuario = self.usuario.get_full_name() or self.usuario.username
        self.nome = self.nome or nome_usuario
        self.email = self.email or self.usuario.email
        self.cargo = self.cargo or self.usuario.cargo
        self.cargo_ref = self.cargo_ref or self.usuario.cargo_ref
        self.funcao_ref = self.funcao_ref or self.usuario.funcao_ref
        self.conselho_ref = self.conselho_ref or self.usuario.conselho_ref
        self.conselho_profissional = (
            self.conselho_profissional or self.usuario.conselho_profissional
        )
        self.registro_profissional = (
            self.registro_profissional or self.usuario.registro_profissional
        )
        self.unidade = self.unidade or self.usuario.unidade

    def sincronizar_campos_normalizados(self):
        if self.cargo_ref_id and not self.cargo:
            self.cargo = self.cargo_ref.nome
        elif self.cargo and not self.cargo_ref_id:
            self.cargo_ref = resolver_cadastro("CargoProfissional", self.cargo)

        if self.funcao_ref_id and not self.funcao:
            self.funcao = self.funcao_ref.nome
        elif self.funcao and not self.funcao_ref_id:
            self.funcao_ref = resolver_cadastro("FuncaoProfissional", self.funcao)

        if self.setor_ref_id and not self.setor:
            self.setor = self.setor_ref.nome
        elif self.setor and not self.setor_ref_id:
            self.setor_ref = resolver_cadastro("SetorHospitalar", self.setor)

        if self.conselho_ref_id and not self.conselho_profissional:
            self.conselho_profissional = self.conselho_ref.codigo
        elif self.conselho_profissional and not self.conselho_ref_id:
            self.conselho_ref = resolver_cadastro(
                "ConselhoProfissional",
                self.conselho_profissional,
            )

        if self.tipo_vinculo_ref_id and not self.tipo_vinculo:
            self.tipo_vinculo = self.tipo_vinculo_ref.codigo
        elif self.tipo_vinculo and not self.tipo_vinculo_ref_id:
            self.tipo_vinculo_ref = resolver_cadastro(
                "TipoVinculoTrabalho",
                self.tipo_vinculo,
            )

    def save(self, *args, **kwargs):
        self.preencher_do_usuario()
        self.sincronizar_campos_normalizados()
        super().save(*args, **kwargs)


class EscalaFuncionario(models.Model):
    MANHA = "MANHA"
    TARDE = "TARDE"
    NOITE = "NOITE"
    PLANTAO_12H = "PLANTAO_12H"
    PLANTAO_24H = "PLANTAO_24H"
    OUTRO = "OUTRO"

    TURNO_CHOICES = [
        (MANHA, "Manha"),
        (TARDE, "Tarde"),
        (NOITE, "Noite"),
        (PLANTAO_12H, "Plantao 12h"),
        (PLANTAO_24H, "Plantao 24h"),
        (OUTRO, "Outro"),
    ]

    PREVISTA = "PREVISTA"
    CONFIRMADA = "CONFIRMADA"
    FALTA = "FALTA"
    TROCA = "TROCA"
    CANCELADA = "CANCELADA"

    STATUS_CHOICES = [
        (PREVISTA, "Prevista"),
        (CONFIRMADA, "Confirmada"),
        (FALTA, "Falta"),
        (TROCA, "Troca"),
        (CANCELADA, "Cancelada"),
    ]

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name="escalas",
    )
    data = models.DateField(db_index=True)
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, default=MANHA)
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_fim = models.TimeField(blank=True, null=True)
    setor_ref = models.ForeignKey(
        "cadastros.SetorHospitalar",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="escalas_funcionarios",
        verbose_name="Setor normalizado",
    )
    setor = models.CharField(
        max_length=80,
        choices=Funcionario.SETOR_CHOICES,
        blank=True,
        default="",
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PREVISTA,
        db_index=True,
    )
    observacoes = models.CharField(max_length=255, blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data", "hora_inicio", "funcionario__nome"]
        verbose_name = "Escala de funcionario"
        verbose_name_plural = "Escalas de funcionarios"
        indexes = [
            models.Index(fields=["data", "setor"], name="escala_data_setor_idx"),
            models.Index(fields=["funcionario", "data"], name="escala_func_data_idx"),
        ]

    def __str__(self):
        return f"{self.funcionario} - {self.data}"


class VinculoFuncionario(models.Model):
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name="vinculos",
    )
    data_admissao = models.DateField(db_index=True)
    data_demissao = models.DateField(blank=True, null=True, db_index=True)
    tipo_vinculo_ref = models.ForeignKey(
        "cadastros.TipoVinculoTrabalho",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="vinculos_funcionarios",
        verbose_name="Tipo de vinculo normalizado",
    )
    tipo_vinculo = models.CharField(
        max_length=20,
        choices=Funcionario.VINCULO_CHOICES,
        blank=True,
        default="",
    )
    cargo_ref = models.ForeignKey(
        "cadastros.CargoProfissional",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="vinculos_funcionarios",
        verbose_name="Cargo normalizado",
    )
    cargo = models.CharField(max_length=100, blank=True, default="")
    setor_ref = models.ForeignKey(
        "cadastros.SetorHospitalar",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="vinculos_funcionarios",
        verbose_name="Setor normalizado",
    )
    setor = models.CharField(
        max_length=80,
        choices=Funcionario.SETOR_CHOICES,
        blank=True,
        default="",
    )
    unidade = models.ForeignKey(
        UnidadeMedica,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="vinculos_funcionarios",
    )
    motivo_demissao = models.CharField(max_length=180, blank=True, default="")
    observacoes = models.TextField(blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data_admissao", "-id"]
        verbose_name = "Vinculo do funcionario"
        verbose_name_plural = "Vinculos dos funcionarios"
        indexes = [
            models.Index(fields=["funcionario", "data_admissao"], name="vinc_func_adm_idx"),
            models.Index(fields=["data_demissao", "funcionario"], name="vinc_dem_func_idx"),
        ]

    def __str__(self):
        fim = self.data_demissao.strftime("%d/%m/%Y") if self.data_demissao else "atual"
        return f"{self.funcionario.nome} - {self.data_admissao:%d/%m/%Y} ate {fim}"

    @property
    def em_aberto(self):
        return self.data_demissao is None
