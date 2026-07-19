from django.contrib import admin

from .models import SolicitacaoAmbulancia


@admin.register(SolicitacaoAmbulancia)
class SolicitacaoAmbulanciaAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "nome_paciente",
        "numero_bam",
        "tipo_transporte",
        "prioridade",
        "status",
        "destino",
        "motorista",
        "veiculo",
        "placa",
        "solicitado_em",
    ]
    list_filter = [
        "status",
        "prioridade",
        "tipo_transporte",
        "necessita_oxigenio",
        "necessita_isolamento",
    ]
    search_fields = [
        "nome_paciente",
        "numero_bam",
        "cpf",
        "destino",
        "unidade_destino",
        "motorista",
        "veiculo",
        "placa",
        "medico_transporte",
        "enfermeiro_transporte",
        "tecnico_transporte",
        "profissional_solicitante",
    ]
    readonly_fields = [
        "solicitado_em",
        "atualizado_em",
        "preparo_em",
        "aguardando_transporte_em",
        "saida_em",
        "concluido_em",
        "cancelado_em",
    ]
