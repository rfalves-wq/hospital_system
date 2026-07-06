from django.urls import path

from . import views


urlpatterns = [
    path("", views.laboratorio_dashboard, name="laboratorio_dashboard"),
    path(
        "resultado/<int:consulta_id>/",
        views.lancar_resultado_laboratorio,
        name="lancar_resultado_laboratorio"
    ),
]