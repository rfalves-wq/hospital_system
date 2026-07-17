from django.contrib.auth.models import AbstractUser
from django.db import models

from .permissions import PAINEL_CHOICES
from unidades.models import UnidadeMedica


class PainelSistema(models.Model):
    codigo = models.CharField(
        max_length=40,
        choices=PAINEL_CHOICES,
        unique=True,
        verbose_name="Painel"
    )
    nome = models.CharField(max_length=120)
    descricao = models.CharField(max_length=255, blank=True, default="")
    ordem = models.PositiveSmallIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordem", "nome"]
        verbose_name = "Painel do sistema"
        verbose_name_plural = "Paineis do sistema"

    def __str__(self):
        return self.nome


class PerfilAcesso(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    descricao = models.CharField(max_length=255, blank=True, default="")
    paineis = models.ManyToManyField(
        PainelSistema,
        blank=True,
        related_name="perfis",
        verbose_name="Paineis liberados"
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Perfil de acesso"
        verbose_name_plural = "Perfis de acesso"

    def __str__(self):
        return self.nome


class Usuario(AbstractUser):

    unidade = models.ForeignKey(
        UnidadeMedica,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    cargo = models.CharField(
        max_length=100,
        blank=True
    )

    perfis_acesso = models.ManyToManyField(
        PerfilAcesso,
        blank=True,
        related_name="usuarios",
        verbose_name="Perfis de acesso"
    )

    paineis_extra = models.ManyToManyField(
        PainelSistema,
        blank=True,
        related_name="usuarios_com_acesso_extra",
        verbose_name="Paineis extras"
    )
