from django.urls import path

from . import views


urlpatterns = [
    path("", views.medicacao_dashboard, name="medicacao_dashboard"),
    path(
        "chamar/<int:consulta_id>/",
        views.chamar_paciente_medicacao,
        name="chamar_paciente_medicacao"
    ),
    path(
        "ausentar/<int:consulta_id>/",
        views.ausentar_paciente_medicacao,
        name="ausentar_paciente_medicacao"
    ),
    path(
        "retornar-ausente/<int:consulta_id>/",
        views.retornar_ausente_medicacao,
        name="retornar_ausente_medicacao"
    ),
    path(
        "administrar/<int:consulta_id>/",
        views.administrar_medicacao,
        name="administrar_medicacao"
    ),
]
