from django.urls import path
from .views import recepcao_dashboard

urlpatterns = [
    path('', recepcao_dashboard, name='recepcao_dashboard'),
]