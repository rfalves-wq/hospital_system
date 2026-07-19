from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("acolhimento", "0021_backfill_permanencia_setor"),
    ]

    operations = [
        migrations.AddField(
            model_name="acolhimento",
            name="medico_atendimento_nome",
            field=models.CharField(
                blank=True,
                default="",
                max_length=150,
                verbose_name="Medico em atendimento",
            ),
        ),
        migrations.AddField(
            model_name="acolhimento",
            name="medico_atendimento_crm",
            field=models.CharField(
                blank=True,
                default="",
                max_length=60,
                verbose_name="CRM do medico em atendimento",
            ),
        ),
        migrations.AddField(
            model_name="acolhimento",
            name="medico_atendimento_consultorio",
            field=models.CharField(
                blank=True,
                default="",
                max_length=80,
                verbose_name="Consultorio do atendimento medico",
            ),
        ),
        migrations.AddField(
            model_name="acolhimento",
            name="medico_atendimento_inicio",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Inicio do atendimento medico",
            ),
        ),
    ]
