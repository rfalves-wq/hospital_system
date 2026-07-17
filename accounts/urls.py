from django.urls import path
from .views import (
    login_view,
    logout_view,
    seguranca_dashboard,
    seguranca_usuario_editar,
    seguranca_usuario_novo,
    seguranca_usuario_status,
    seguranca_usuarios,
)

urlpatterns = [
    path('', login_view, name='login'),
    path('sair/', logout_view, name='logout'),
    path('seguranca/', seguranca_dashboard, name='seguranca_dashboard'),
    path('seguranca/usuarios/', seguranca_usuarios, name='seguranca_usuarios'),
    path(
        'seguranca/usuarios/novo/',
        seguranca_usuario_novo,
        name='seguranca_usuario_novo'
    ),
    path(
        'seguranca/usuarios/<int:usuario_id>/editar/',
        seguranca_usuario_editar,
        name='seguranca_usuario_editar'
    ),
    path(
        'seguranca/usuarios/<int:usuario_id>/status/',
        seguranca_usuario_status,
        name='seguranca_usuario_status'
    ),
]
