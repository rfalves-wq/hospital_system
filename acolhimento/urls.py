from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.tipo_atendimento,
        name="tipo_atendimento"
    ),

    path(
        "buscar-paciente/",
        views.buscar_paciente,
        name="buscar_paciente"
    ),

    path(
        "normal/",
        views.atendimento_normal,
        name="atendimento_normal"
    ),

    path(
        "risco/",
        views.triagem_risco,
        name="triagem_risco"
    ),

    path(
        "preferencial/",
        views.atendimento_preferencial,
        name="atendimento_preferencial"
    ),
    path(
    "reenviar-recepcao/<int:acolhimento_id>/",
    views.reenviar_para_recepcao,
    name="acolhimento_reenviar_recepcao"
),
    
]