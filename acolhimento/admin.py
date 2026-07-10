from django.contrib import admin
from .models import Acolhimento


@admin.register(Acolhimento)
class AcolhimentoAdmin(admin.ModelAdmin):

    list_display = (
        'nome_paciente',
        'cpf',
        'tipo_atendimento',
        'hora_chegada',
        'chamadas_classificacao',
        'ausente_classificacao',
        'data_acolhimento'
    )

    search_fields = (
        'nome_paciente',
        'cpf'
    )
