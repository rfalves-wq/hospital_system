from django.contrib import admin

from .models import EvolucaoInternacao, Internacao, LeitoInternacao, SetorInternacao


@admin.register(SetorInternacao)
class SetorInternacaoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "ativo", "ordem")
    list_filter = ("ativo",)
    search_fields = ("codigo", "nome")


@admin.register(LeitoInternacao)
class LeitoInternacaoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "setor", "tipo", "status_operacional", "ordem")
    list_filter = ("setor", "tipo", "status_operacional")
    search_fields = ("codigo", "setor__nome")


class EvolucaoInternacaoInline(admin.TabularInline):
    model = EvolucaoInternacao
    extra = 0


@admin.register(Internacao)
class InternacaoAdmin(admin.ModelAdmin):
    list_display = (
        "acolhimento",
        "leito",
        "setor",
        "status",
        "data_internacao",
        "data_alta",
    )
    list_filter = ("status", "setor")
    search_fields = (
        "acolhimento__numero_bam",
        "acolhimento__nome_paciente",
        "leito",
        "setor",
    )
    inlines = [EvolucaoInternacaoInline]


@admin.register(EvolucaoInternacao)
class EvolucaoInternacaoAdmin(admin.ModelAdmin):
    list_display = (
        "internacao",
        "data_evolucao",
        "profissional",
    )
    search_fields = (
        "internacao__acolhimento__numero_bam",
        "internacao__acolhimento__nome_paciente",
        "profissional",
    )
