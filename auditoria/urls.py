from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="auditoria_dashboard"),
    path("exportar/", views.exportar_csv, name="auditoria_exportar"),
]
