from django.urls import path

from . import views


urlpatterns = [
    path("", views.prontuario_dashboard, name="prontuario_dashboard"),
    path("paciente/<int:paciente_id>/", views.prontuario_paciente, name="prontuario_paciente"),
    path("atendimento/<int:acolhimento_id>/", views.prontuario_atendimento, name="prontuario_atendimento"),
]
