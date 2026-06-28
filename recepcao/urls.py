from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.recepcao_dashboard,
        name="recepcao_dashboard"
    ),

    path(
        "cadastrar/<int:acolhimento_id>/",
        views.cadastrar_paciente,
        name="cadastrar_paciente"
    ),

]