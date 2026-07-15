from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("acolhimento", "0015_acolhimento_chamada_classificacao"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ChamadaPainel",
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
                (
                    "setor",
                    models.CharField(
                        choices=[
                            ("RECEPCAO", "Recepcao"),
                            ("CLASSIFICACAO", "Classificacao de risco"),
                            ("MEDICO", "Medico"),
                            ("MEDICACAO", "Sala de medicacao"),
                        ],
                        max_length=30,
                    ),
                ),
                ("numero_bam", models.CharField(blank=True, default="", max_length=30)),
                ("paciente_nome", models.CharField(max_length=200)),
                ("local_destino", models.CharField(blank=True, default="", max_length=120)),
                ("observacao", models.CharField(blank=True, default="", max_length=160)),
                ("chamado_por_nome", models.CharField(blank=True, default="", max_length=120)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                (
                    "acolhimento",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="chamadas_painel",
                        to="acolhimento.acolhimento",
                    ),
                ),
                (
                    "chamado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="chamadas_painel_realizadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Chamada do painel",
                "verbose_name_plural": "Chamadas do painel",
                "ordering": ["-criado_em"],
            },
        ),
    ]
