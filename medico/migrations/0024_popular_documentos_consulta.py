from django.db import migrations


def criar_documento(Document, consulta, tipo, texto, dias_atestado=None, cid_codigo=""):
    texto = texto or ""
    cid_codigo = (cid_codigo or "").strip().upper()

    if not texto and not dias_atestado and not cid_codigo:
        return

    Document.objects.update_or_create(
        consulta=consulta,
        tipo=tipo,
        defaults={
            "texto": texto,
            "dias_atestado": dias_atestado,
            "cid_codigo": cid_codigo,
            "profissional_nome": consulta.medico_responsavel,
            "profissional_registro": consulta.crm_medico or "",
        },
    )


def popular_documentos(apps, schema_editor):
    Consulta = apps.get_model("medico", "ConsultaMedica")
    Document = apps.get_model("medico", "DocumentoConsultaMedica")
    CID = apps.get_model("medico", "CID")

    for consulta in Consulta.objects.all().iterator():
        criar_documento(Document, consulta, "PRESCRICAO", consulta.prescricao)
        criar_documento(Document, consulta, "RECEITA", consulta.receita)

        atestado_cid = (consulta.atestado_cid or "").strip().upper()
        cid = CID.objects.filter(codigo__iexact=atestado_cid).first() if atestado_cid else None
        if consulta.atestado or consulta.atestado_dias or atestado_cid:
            Document.objects.update_or_create(
                consulta=consulta,
                tipo="ATESTADO",
                defaults={
                    "texto": consulta.atestado or "",
                    "dias_atestado": consulta.atestado_dias,
                    "cid": cid,
                    "cid_codigo": atestado_cid,
                    "profissional_nome": consulta.medico_responsavel,
                    "profissional_registro": consulta.crm_medico or "",
                },
            )

        criar_documento(Document, consulta, "ORIENTACAO", consulta.orientacoes)


class Migration(migrations.Migration):
    dependencies = [
        ("medico", "0023_documentoconsultamedica"),
    ]

    operations = [
        migrations.RunPython(popular_documentos, migrations.RunPython.noop),
    ]
