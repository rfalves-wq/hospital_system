from django.urls import path

from . import views


urlpatterns = [
    path("", views.farmacia_dashboard, name="farmacia_dashboard"),
    path(
        "liberar/<int:consulta_id>/",
        views.liberar_medicacao,
        name="liberar_medicacao_farmacia"
    ),
    path(
        "estoque/buscar/",
        views.buscar_medicamento_estoque,
        name="farmacia_buscar_medicamento_estoque"
    ),
    path(
        "estoque/",
        views.estoque_dashboard,
        name="farmacia_estoque"
    ),
    path(
        "estoque/novo/",
        views.cadastrar_medicamento,
        name="farmacia_medicamento_novo"
    ),
    path(
        "estoque/<int:medicamento_id>/editar/",
        views.cadastrar_medicamento,
        name="farmacia_medicamento_editar"
    ),
    path(
        "estoque/<int:medicamento_id>/<str:tipo>/",
        views.movimentar_estoque,
        name="farmacia_movimentar_estoque"
    ),
]
