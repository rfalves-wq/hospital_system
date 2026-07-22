from django.db import models
from django.utils.text import slugify


def normalizar_codigo(valor, tamanho=50):
    codigo = slugify(valor or "", allow_unicode=False).upper().replace("-", "_")
    return (codigo or "SEM_CODIGO")[:tamanho]


class CadastroNormalizado(models.Model):
    codigo = models.CharField(max_length=50, unique=True, db_index=True)
    nome = models.CharField(max_length=160, unique=True)
    descricao = models.CharField(max_length=255, blank=True, default="")
    ativo = models.BooleanField(default=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["nome"]

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = normalizar_codigo(self.nome)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class ConselhoProfissional(CadastroNormalizado):
    class Meta(CadastroNormalizado.Meta):
        verbose_name = "Conselho profissional"
        verbose_name_plural = "Conselhos profissionais"


class SetorHospitalar(CadastroNormalizado):
    ASSISTENCIAL = "ASSISTENCIAL"
    ADMINISTRATIVO = "ADMINISTRATIVO"
    APOIO = "APOIO"
    ESTOQUE = "ESTOQUE"
    OUTRO = "OUTRO"

    TIPO_CHOICES = [
        (ASSISTENCIAL, "Assistencial"),
        (ADMINISTRATIVO, "Administrativo"),
        (APOIO, "Apoio"),
        (ESTOQUE, "Estoque"),
        (OUTRO, "Outro"),
    ]

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default=ASSISTENCIAL,
        db_index=True,
    )

    class Meta(CadastroNormalizado.Meta):
        verbose_name = "Setor hospitalar"
        verbose_name_plural = "Setores hospitalares"
        indexes = [
            models.Index(fields=["ativo", "tipo", "nome"], name="setor_ativo_tipo_idx"),
        ]


class CargoProfissional(CadastroNormalizado):
    conselho_padrao = models.ForeignKey(
        ConselhoProfissional,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="cargos_padrao",
    )

    class Meta(CadastroNormalizado.Meta):
        verbose_name = "Cargo profissional"
        verbose_name_plural = "Cargos profissionais"


class FuncaoProfissional(CadastroNormalizado):
    cargo = models.ForeignKey(
        CargoProfissional,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="funcoes",
    )
    setor_padrao = models.ForeignKey(
        SetorHospitalar,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="funcoes_padrao",
    )

    class Meta(CadastroNormalizado.Meta):
        verbose_name = "Funcao profissional"
        verbose_name_plural = "Funcoes profissionais"
        constraints = [
            models.UniqueConstraint(
                fields=["cargo", "nome"],
                name="funcao_unica_por_cargo",
            ),
        ]


class TipoVinculoTrabalho(CadastroNormalizado):
    class Meta(CadastroNormalizado.Meta):
        verbose_name = "Tipo de vinculo de trabalho"
        verbose_name_plural = "Tipos de vinculo de trabalho"
