from django.urls import path

from . import views


urlpatterns = [
    path("", views.tecnologia_dashboard, name="tecnologia_dashboard"),
    path(
        "pedido-servico/",
        views.pedido_servico_ti,
        name="tecnologia_pedido_servico"
    ),
    path(
        "chamados/",
        views.tecnologia_chamados,
        name="tecnologia_chamados"
    ),
    path("status/", views.tecnologia_status, name="tecnologia_status"),
]
