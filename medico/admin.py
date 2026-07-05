from django.contrib import admin

from .models import ConsultaMedica, CID


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