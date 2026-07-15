import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("acolhimento", "0017_acolhimento_data_ausente_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("medico", "0018_transferenciaconsultamedica"),
    ]

    operations = [
        migrations.CreateModel(
            name="AlertaPanicoMedico",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("medico_nome", models.CharField(max_length=150)),
                ("consultorio", models.CharField(blank=True, default="", max_length=80)),
                ("paciente_nome", models.CharField(blank=True, default="", max_length=200)),
                ("numero_bam", models.CharField(blank=True, default="", max_length=20)),
                ("mensagem", models.CharField(blank=True, default="", max_length=255)),
                ("ativo", models.BooleanField(db_index=True, default=True)),
                (
                    "criado_em",
                    models.DateTimeField(
                        db_index=True,
                        default=django.utils.timezone.now,
                    ),
                ),
                ("encerrado_em", models.DateTimeField(blank=True, null=True)),
                ("encerrado_por", models.CharField(blank=True, default="", max_length=150)),
                (
                    "acolhimento",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="alertas_panico_medico",
                        to="acolhimento.acolhimento",
                    ),
                ),
                (
                    "medico",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="alertas_panico_medico",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Alerta de pânico médico",
                "verbose_name_plural": "Alertas de pânico médico",
                "ordering": ["-criado_em"],
            },
        ),
    ]
