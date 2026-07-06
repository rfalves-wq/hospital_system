from django.urls import path

from . import views


urlpatterns = [
    path("", views.imagem_dashboard, name="imagem_dashboard"),
    path(
        "resultado/<int:consulta_id>/<str:setor>/",
        views.lancar_resultado_imagem,
        name="lancar_resultado_imagem"
    ),
]