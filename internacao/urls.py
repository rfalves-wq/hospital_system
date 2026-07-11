from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.internacao_dashboard,
        name="internacao_dashboard"
    ),
    path(
        "registrar/<int:acolhimento_id>/",
        views.registrar_internacao,
        name="registrar_internacao"
    ),
    path(
        "detalhe/<int:internacao_id>/",
        views.detalhe_internacao,
        name="detalhe_internacao"
    ),
]
