from django.db import models

class UnidadeMedica(models.Model):

    nome = models.CharField(
        max_length=200
    )

    endereco = models.CharField(
        max_length=300
    )

    telefone = models.CharField(
        max_length=20
    )

    def __str__(self):
        return self.nome