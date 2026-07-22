from django.contrib import admin

from .models import MaterialAlmoxarifado, MovimentacaoAlmoxarifado


@admin.register(MaterialAlmoxarifado)
class MaterialAlmoxarifadoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "categoria",
        "codigo",
        "estoque_atual",
        "estoque_minimo",
        "localizacao",
        "ativo",
    )
    list_filter = ("categoria", "ativo", "validade")
    search_fields = ("nome", "codigo", "descricao", "marca", "fornecedor", "localizacao")


@admin.register(MovimentacaoAlmoxarifado)
class MovimentacaoAlmoxarifadoAdmin(admin.ModelAdmin):
    list_display = (
        "tipo",
        "material",
        "quantidade",
        "saldo_anterior",
        "saldo_atual",
        "setor_destino",
        "profissional_nome",
        "criado_em",
    )
    list_filter = ("tipo", "setor_destino", "criado_em")
    search_fields = ("material__nome", "material__codigo", "origem_destino", "solicitante_nome", "profissional_nome")
