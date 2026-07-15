from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def vincular_chamados_antigos(apps, schema_editor):
    Chamado = apps.get_model("tecnologia", "ChamadoManutencaoTI")
    Usuario = apps.get_model("accounts", "Usuario")

    usuarios = list(Usuario.objects.all())

    for chamado in Chamado.objects.filter(solicitante__isnull=True):
        nome_salvo = (chamado.solicitado_por or "").strip()

        if not nome_salvo:
            continue

        usuario = Usuario.objects.filter(username=nome_salvo).first()

        if not usuario:
            for candidato in usuarios:
                nome_completo = (
                    f"{candidato.first_name} {candidato.last_name}"
                ).strip()

                if nome_completo and nome_completo == nome_salvo:
                    usuario = candidato
                    break

        if usuario:
            chamado.solicitante = usuario
            chamado.save(update_fields=["solicitante"])


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tecnologia", "0008_chamado_resposta_ti"),
    ]

    operations = [
        migrations.AddField(
            model_name="chamadomanutencaoti",
            name="solicitante",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="chamados_ti_solicitados",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(
            vincular_chamados_antigos,
            migrations.RunPython.noop,
        ),
    ]
