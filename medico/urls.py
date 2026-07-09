from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.medico_dashboard,
        name="medico_dashboard"
    ),

    path(
        "buscar-cid/",
        views.buscar_cid,
        name="buscar_cid"
    ),

    path(
        "buscar-medicamento-farmacia/",
        views.buscar_medicamento_farmacia,
        name="buscar_medicamento_farmacia"
    ),

    path(
        "atender/<int:acolhimento_id>/",
        views.atender_paciente,
        name="atender_paciente"
    ),

    path(
        "retornar/<int:acolhimento_id>/",
        views.retornar_para_medico,
        name="retornar_para_medico"
    ),
]
