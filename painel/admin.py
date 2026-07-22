from django.contrib import admin

from .models import ChamadaPainel


@admin.register(ChamadaPainel)
class ChamadaPainelAdmin(admin.ModelAdmin):
    list_display = (
        "tipo",
        "paciente_nome",
        "numero_bam",
        "setor",
        "local_destino",
        "visivel_painel",
        "chamado_por_nome",
        "criado_em",
    )
    list_filter = ("tipo", "setor", "visivel_painel", "criado_em")
    search_fields = ("paciente_nome", "numero_bam", "local_destino")
