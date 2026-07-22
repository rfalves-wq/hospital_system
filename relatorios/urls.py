from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="relatorios_dashboard"),
    path("exportar/", views.exportar_csv, name="relatorios_exportar"),
]
