from django.contrib import admin

from .models import EscalaFuncionario, Funcionario, VinculoFuncionario


class EscalaFuncionarioInline(admin.TabularInline):
    model = EscalaFuncionario
    extra = 0


class VinculoFuncionarioInline(admin.TabularInline):
    model = VinculoFuncionario
    extra = 0


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "cargo",
        "cargo_ref",
        "setor",
        "setor_ref",
        "conselho_profissional",
        "conselho_ref",
        "registro_profissional",
        "ativo",
    )
    list_filter = ("ativo", "setor_ref", "cargo_ref", "setor", "cargo", "conselho_profissional")
    search_fields = ("nome", "cpf", "matricula", "registro_profissional", "usuario__username")
    inlines = [VinculoFuncionarioInline, EscalaFuncionarioInline]


@admin.register(EscalaFuncionario)
class EscalaFuncionarioAdmin(admin.ModelAdmin):
    list_display = ("data", "funcionario", "turno", "setor", "setor_ref", "status", "hora_inicio", "hora_fim")
    list_filter = ("data", "setor_ref", "setor", "status", "turno")
    search_fields = ("funcionario__nome", "observacoes")


@admin.register(VinculoFuncionario)
class VinculoFuncionarioAdmin(admin.ModelAdmin):
    list_display = ("funcionario", "data_admissao", "data_demissao", "cargo", "cargo_ref", "setor", "setor_ref", "tipo_vinculo")
    list_filter = ("setor_ref", "setor", "tipo_vinculo_ref", "tipo_vinculo", "data_admissao", "data_demissao")
    search_fields = ("funcionario__nome", "cargo", "motivo_demissao")
