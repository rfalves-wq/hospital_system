from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="funcionarios_dashboard"),
    path("<int:funcionario_id>/editar/", views.editar, name="funcionarios_editar"),
    path("<int:funcionario_id>/status/", views.alterar_status, name="funcionarios_status"),
    path("sincronizar-logins/", views.sincronizar_logins, name="funcionarios_sincronizar"),
]
