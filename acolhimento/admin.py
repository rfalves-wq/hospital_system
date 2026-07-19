from django.contrib import admin
from .models import Acolhimento, PermanenciaSetorAtendimento


@admin.register(Acolhimento)
class AcolhimentoAdmin(admin.ModelAdmin):

    list_display = (
        'nome_paciente',
        'cpf',
        'tipo_atendimento',
        'hora_chegada',
        'chamadas_classificacao',
        'ausente_classificacao',
        'medico_atendimento_nome',
        'medico_atendimento_inicio',
        'data_acolhimento'
    )

    search_fields = (
        'nome_paciente',
        'cpf',
        'medico_atendimento_nome',
    )


@admin.register(PermanenciaSetorAtendimento)
class PermanenciaSetorAtendimentoAdmin(admin.ModelAdmin):
    list_display = (
        "acolhimento",
        "setor",
        "origem",
        "entrada",
        "saida",
        "duracao_formatada",
    )
    list_filter = (
        "setor",
        "origem",
        "saida",
    )
    search_fields = (
        "acolhimento__numero_bam",
        "acolhimento__nome_paciente",
        "acolhimento__cpf",
    )
    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )
