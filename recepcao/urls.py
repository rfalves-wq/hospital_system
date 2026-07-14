from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.recepcao_dashboard,
        name="recepcao_dashboard"
    ),

    path(
        "api/cidades/<str:uf>/",
        views.cidades_por_uf,
        name="recepcao_cidades_por_uf"
    ),

    path(
        "cadastrar/<int:acolhimento_id>/",
        views.cadastrar_paciente,
        name="cadastrar_paciente"
    ),
    
      path(
        "classificacao/<int:acolhimento_id>/",
        views.enviar_classificacao,
        name="enviar_classificacao"
    ),

]
