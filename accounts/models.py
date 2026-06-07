from django.contrib.auth.models import AbstractUser
from django.db import models

from unidades.models import UnidadeMedica

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