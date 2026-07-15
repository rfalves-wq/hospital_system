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
        "consultorio/",
        views.definir_consultorio_medico,
        name="definir_consultorio_medico"
    ),

    path(
        "panico/acionar/",
        views.acionar_panico_medico,
        name="acionar_panico_medico"
    ),

    path(
        "panico/status/",
        views.status_panico_medico,
        name="status_panico_medico"
    ),

    path(
        "panico/encerrar/",
        views.encerrar_panico_medico,
        name="encerrar_panico_medico"
    ),

    path(
        "atender/<int:acolhimento_id>/",
        views.atender_paciente,
        name="atender_paciente"
    ),

    path(
        "chamar/<int:acolhimento_id>/",
        views.chamar_paciente_medico,
        name="chamar_paciente_medico"
    ),

    path(
        "ausentar/<int:acolhimento_id>/",
        views.ausentar_paciente_medico,
        name="ausentar_paciente_medico"
    ),

    path(
        "retornar-ausente/<int:acolhimento_id>/",
        views.retornar_ausente_medico,
        name="retornar_ausente_medico"
    ),

    path(
        "assumir/<int:acolhimento_id>/",
        views.assumir_paciente,
        name="assumir_paciente_medico"
    ),

    path(
        "retornar/<int:acolhimento_id>/",
        views.retornar_para_medico,
        name="retornar_para_medico"
    ),
]
