from django.contrib import admin

from .models import MedicamentoEstoque, MovimentacaoEstoque


@admin.register(MedicamentoEstoque)
class MedicamentoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "categoria",
        "metodo_aplicacao",
        "principio_ativo",
        "apresentacao",
        "concentracao",
        "estoque_atual",
        "estoque_minimo",
        "ativo",
    )
    list_filter = ("ativo", "categoria", "metodo_aplicacao", "apresentacao")
    search_fields = ("nome", "principio_ativo", "concentracao")


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "criado_em",
        "tipo",
        "medicamento",
        "quantidade",
        "saldo_anterior",
        "saldo_atual",
        "profissional_nome",
    )
    list_filter = ("tipo", "criado_em")
    search_fields = ("medicamento__nome", "profissional_nome", "lote")
    autocomplete_fields = ("medicamento",)
