from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="ambulancia_dashboard"),
    path("<int:solicitacao_id>/dados/", views.atualizar_dados_transporte, name="ambulancia_atualizar_dados"),
    path("<int:solicitacao_id>/status/", views.alterar_status, name="ambulancia_alterar_status"),
    path("<int:solicitacao_id>/imprimir/", views.imprimir_solicitacao, name="ambulancia_imprimir"),
]
