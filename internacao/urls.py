from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.internacao_dashboard,
        name="internacao_dashboard"
    ),
    path(
        "leitos/",
        views.gestao_leitos,
        name="gestao_leitos"
    ),
    path(
        "leitos/<int:leito_id>/status/",
        views.alterar_status_leito,
        name="alterar_status_leito"
    ),
    path(
        "setores/<int:setor_id>/status/",
        views.alterar_status_setor,
        name="alterar_status_setor"
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
