from django.contrib import admin

from .models import EventoAuditoria


@admin.register(EventoAuditoria)
class EventoAuditoriaAdmin(admin.ModelAdmin):
    list_display = (
        "criado_em",
        "acao",
        "modulo",
        "profissional",
        "usuario_login",
        "numero_bam",
        "status_code",
    )
    list_filter = ("acao", "modulo", "status_code", "criado_em")
    search_fields = (
        "profissional",
        "usuario_login",
        "numero_bam",
        "nome_paciente",
        "caminho",
        "descricao",
    )
    readonly_fields = [field.name for field in EventoAuditoria._meta.fields]
    date_hierarchy = "criado_em"
