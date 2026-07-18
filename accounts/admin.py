from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

from .models import PainelSistema, PerfilAcesso, Usuario


@admin.register(PainelSistema)
class PainelSistemaAdmin(admin.ModelAdmin):
    list_display = [
        "nome",
        "codigo",
        "ativo",
        "ordem",
    ]
    list_editable = [
        "ativo",
        "ordem",
    ]
    search_fields = [
        "nome",
        "codigo",
        "descricao",
    ]
    list_filter = [
        "ativo",
    ]


@admin.register(PerfilAcesso)
class PerfilAcessoAdmin(admin.ModelAdmin):
    list_display = [
        "nome",
        "ativo",
    ]
    search_fields = [
        "nome",
        "descricao",
    ]
    list_filter = [
        "ativo",
    ]
    filter_horizontal = [
        "paineis",
    ]


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UserChangeForm
    add_form = AdminUserCreationForm
    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "cargo",
        "conselho_profissional",
        "registro_profissional",
        "is_active",
        "is_staff",
    ]
    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
        "perfis_acesso",
        "paineis_extra",
    ]
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "cargo",
        "conselho_profissional",
        "registro_profissional",
    ]
    filter_horizontal = [
        "groups",
        "user_permissions",
        "perfis_acesso",
        "paineis_extra",
    ]
    fieldsets = UserAdmin.fieldsets + (
        (
            "Dados do hospital",
            {
                "fields": (
                    "unidade",
                    "cargo",
                    "conselho_profissional",
                    "registro_profissional",
                )
            },
        ),
        (
            "Acessos aos paineis",
            {
                "fields": (
                    "perfis_acesso",
                    "paineis_extra",
                ),
                "description": (
                    "Defina um ou mais perfis para o usuario. "
                    "Use paineis extras quando quiser liberar um painel fora do perfil."
                ),
            },
        ),
    )
