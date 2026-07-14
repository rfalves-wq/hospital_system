from django.contrib import admin

from .models import EquipamentoTI


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
