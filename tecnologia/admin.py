from django.contrib import admin

from .models import ChamadoManutencaoTI, EquipamentoTI


@admin.register(EquipamentoTI)
class EquipamentoTIAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "tipo",
        "setor",
        "endereco_rede",
        "mac_address",
        "origem_ip",
        "ultimo_status",
        "ultima_verificacao",
        "ativo",
    )
    list_filter = ("tipo", "origem_ip", "ultimo_status", "ativo")
    search_fields = ("nome", "setor", "endereco_rede", "mac_address")


@admin.register(ChamadoManutencaoTI)
class ChamadoManutencaoTIAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "tipo_servico",
        "equipamento",
        "setor_solicitante",
        "prioridade",
        "status",
        "solicitado_por",
        "solicitante",
        "respondido_por",
        "respondido_em",
        "criado_em",
        "concluido_em",
    )
    list_filter = ("tipo_servico", "prioridade", "status", "criado_em")
    search_fields = (
        "titulo",
        "descricao",
        "setor_solicitante",
        "contato",
        "solicitado_por",
        "solicitante__username",
        "solicitante__first_name",
        "solicitante__last_name",
        "resposta_ti",
        "respondido_por",
        "equipamento__nome",
        "equipamento__endereco_rede",
    )
