from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.classificacao_dashboard,
        name="classificacao_dashboard"
    ),

]