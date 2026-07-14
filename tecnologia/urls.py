from django.urls import path

from . import views


urlpatterns = [
    path("", views.tecnologia_dashboard, name="tecnologia_dashboard"),
    path("status/", views.tecnologia_status, name="tecnologia_status"),
]
