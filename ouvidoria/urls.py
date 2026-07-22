from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="ouvidoria_dashboard"),
    path("nova/", views.formulario, name="ouvidoria_nova"),
    path("<int:manifestacao_id>/", views.formulario, name="ouvidoria_editar"),
    path("<int:manifestacao_id>/andamento/", views.registrar_andamento, name="ouvidoria_andamento"),
]
