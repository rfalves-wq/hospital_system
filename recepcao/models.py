from django.db import models
from paciente.models import Paciente


class RegistroRecepcao(models.Model):

    STATUS_CHOICES = [
        ('AGUARDANDO', 'Aguardando'),
        ('CADASTRADO', 'Cadastrado'),
        ('ENCAMINHADO', 'Encaminhado'),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE
    )

    data_entrada = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AGUARDANDO'
    )

    observacao = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.paciente.nome