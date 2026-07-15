from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.classificacao_dashboard,
        name="classificacao_dashboard"
    ),

    path(
        "classificar/<int:acolhimento_id>/",
        views.classificar_paciente,
        name="classificar_paciente"
    ),

    path(
        "chamar/<int:acolhimento_id>/",
        views.chamar_paciente_classificacao,
        name="chamar_paciente_classificacao"
    ),

    path(
        "ausentar/<int:acolhimento_id>/",
        views.ausentar_paciente_classificacao,
        name="ausentar_paciente_classificacao"
    ),

    path(
        "retornar-ausente/<int:acolhimento_id>/",
        views.retornar_ausente_classificacao,
        name="retornar_ausente_classificacao"
    ),

]
