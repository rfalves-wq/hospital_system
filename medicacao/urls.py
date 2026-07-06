from django.urls import path

from . import views


urlpatterns = [
    path("", views.medicacao_dashboard, name="medicacao_dashboard"),
    path(
        "administrar/<int:consulta_id>/",
        views.administrar_medicacao,
        name="administrar_medicacao"
    ),
]