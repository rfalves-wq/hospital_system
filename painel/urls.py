from django.urls import path

from . import views


urlpatterns = [
    path("", views.painel_chamados, name="painel_chamados"),
    path("dados/", views.painel_chamados_dados, name="painel_chamados_dados"),
]
