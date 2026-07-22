from django.contrib import admin

from .models import (
    CargoProfissional,
    ConselhoProfissional,
    FuncaoProfissional,
    SetorHospitalar,
    TipoVinculoTrabalho,
)


@admin.register(ConselhoProfissional)
class ConselhoProfissionalAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nome", "ativo"]
    list_filter = ["ativo"]
    search_fields = ["codigo", "nome"]


@admin.register(SetorHospitalar)
class SetorHospitalarAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nome", "tipo", "ativo"]
    list_filter = ["tipo", "ativo"]
    search_fields = ["codigo", "nome"]


@admin.register(CargoProfissional)
class CargoProfissionalAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nome", "conselho_padrao", "ativo"]
    list_filter = ["ativo", "conselho_padrao"]
    search_fields = ["codigo", "nome"]


@admin.register(FuncaoProfissional)
class FuncaoProfissionalAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nome", "cargo", "setor_padrao", "ativo"]
    list_filter = ["ativo", "cargo", "setor_padrao"]
    search_fields = ["codigo", "nome", "cargo__nome"]


@admin.register(TipoVinculoTrabalho)
class TipoVinculoTrabalhoAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nome", "ativo"]
    list_filter = ["ativo"]
    search_fields = ["codigo", "nome"]
