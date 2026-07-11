from django.contrib import admin

from .models import ConsultaMedica, CID, TransferenciaConsultaMedica


@admin.register(CID)
class CIDAdmin(admin.ModelAdmin):
    list_display = [
        "codigo",
        "descricao",
        "tipo",
    ]

    search_fields = [
        "codigo",
        "descricao",
    ]

    list_filter = [
        "tipo",
    ]


@admin.register(ConsultaMedica)
class ConsultaMedicaAdmin(admin.ModelAdmin):
    list_display = [
        "acolhimento",
        "medico_responsavel",
        "cid",
        "conduta",
        "data_consulta",
    ]

    search_fields = [
        "acolhimento__nome_paciente",
        "medico_responsavel",
        "cid",
        "hipotese_diagnostica",
    ]

    list_filter = [
        "conduta",
        "data_consulta",
    ]


@admin.register(TransferenciaConsultaMedica)
class TransferenciaConsultaMedicaAdmin(admin.ModelAdmin):
    list_display = [
        "consulta",
        "medico_anterior",
        "medico_novo",
        "motivo",
        "data_transferencia",
    ]

    search_fields = [
        "consulta__acolhimento__numero_bam",
        "consulta__acolhimento__nome_paciente",
        "medico_anterior",
        "medico_novo",
    ]

    list_filter = [
        "motivo",
        "data_transferencia",
    ]
