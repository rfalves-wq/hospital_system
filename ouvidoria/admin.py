from django.contrib import admin

from .models import AndamentoOuvidoria, ManifestacaoOuvidoria


class AndamentoInline(admin.TabularInline):
    model = AndamentoOuvidoria
    extra = 0
    readonly_fields = ("criado_em",)


@admin.register(ManifestacaoOuvidoria)
class ManifestacaoOuvidoriaAdmin(admin.ModelAdmin):
    list_display = (
        "protocolo",
        "nome_manifestante",
        "tipo",
        "prioridade",
        "status",
        "setor_envolvido",
        "prazo_resposta",
        "criado_em",
    )
    list_filter = ("status", "tipo", "prioridade", "setor_envolvido", "canal")
    search_fields = (
        "protocolo",
        "nome_manifestante",
        "cpf_manifestante",
        "numero_bam",
        "paciente_nome",
        "titulo",
    )
    readonly_fields = ("protocolo", "criado_em", "atualizado_em", "respondido_em", "concluido_em")
    inlines = [AndamentoInline]


@admin.register(AndamentoOuvidoria)
class AndamentoOuvidoriaAdmin(admin.ModelAdmin):
    list_display = ("manifestacao", "status", "profissional_nome", "criado_em")
    list_filter = ("status",)
    search_fields = ("manifestacao__protocolo", "anotacao", "profissional_nome")
