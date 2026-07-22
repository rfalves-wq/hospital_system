from django.contrib import admin

from .models import (
    EquipamentoMedicoAmbulancia,
    EquipamentoSolicitacaoAmbulancia,
    MembroEquipeAmbulancia,
    SolicitacaoAmbulancia,
)


class MembroEquipeAmbulanciaInline(admin.TabularInline):
    model = MembroEquipeAmbulancia
    extra = 0


class EquipamentoSolicitacaoAmbulanciaInline(admin.TabularInline):
    model = EquipamentoSolicitacaoAmbulancia
    extra = 0


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
    inlines = [
        MembroEquipeAmbulanciaInline,
        EquipamentoSolicitacaoAmbulanciaInline,
    ]


@admin.register(MembroEquipeAmbulancia)
class MembroEquipeAmbulanciaAdmin(admin.ModelAdmin):
    list_display = ["solicitacao", "papel", "nome", "conselho", "registro"]
    list_filter = ["papel"]
    search_fields = ["solicitacao__nome_paciente", "solicitacao__numero_bam", "nome"]


@admin.register(EquipamentoMedicoAmbulancia)
class EquipamentoMedicoAmbulanciaAdmin(admin.ModelAdmin):
    list_display = ["nome", "ativo"]
    list_filter = ["ativo"]
    search_fields = ["nome", "descricao"]


@admin.register(EquipamentoSolicitacaoAmbulancia)
class EquipamentoSolicitacaoAmbulanciaAdmin(admin.ModelAdmin):
    list_display = ["solicitacao", "equipamento", "quantidade", "conferido_saida", "conferido_chegada"]
    list_filter = ["conferido_saida", "conferido_chegada"]
    search_fields = ["solicitacao__nome_paciente", "solicitacao__numero_bam", "equipamento__nome"]
