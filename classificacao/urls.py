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

]