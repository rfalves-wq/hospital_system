from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="almoxarifado_dashboard"),
    path("material/novo/", views.cadastrar_material, name="almoxarifado_material_novo"),
    path("material/<int:material_id>/editar/", views.cadastrar_material, name="almoxarifado_material_editar"),
    path("material/<int:material_id>/<str:tipo>/", views.movimentar_material, name="almoxarifado_movimentar"),
]
