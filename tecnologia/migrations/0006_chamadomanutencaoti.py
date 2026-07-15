from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tecnologia", "0005_tipo_camera_dvr"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChamadoManutencaoTI",
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
                ("titulo", models.CharField(max_length=140)),
                ("descricao", models.TextField(blank=True, default="")),
                (
                    "prioridade",
                    models.CharField(
                        choices=[
                            ("BAIXA", "Baixa"),
                            ("NORMAL", "Normal"),
                            ("ALTA", "Alta"),
                            ("URGENTE", "Urgente"),
                        ],
                        default="NORMAL",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ABERTO", "Aberto"),
                            ("EM_ANDAMENTO", "Em andamento"),
                            ("CONCLUIDO", "Concluido"),
                            ("CANCELADO", "Cancelado"),
                        ],
                        default="ABERTO",
                        max_length=20,
                    ),
                ),
                ("solicitado_por", models.CharField(blank=True, default="", max_length=120)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("concluido_em", models.DateTimeField(blank=True, null=True)),
                (
                    "equipamento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chamados_manutencao",
                        to="tecnologia.equipamentoti",
                    ),
                ),
            ],
            options={
                "verbose_name": "Chamado de manutencao de TI",
                "verbose_name_plural": "Chamados de manutencao de TI",
                "ordering": ["-criado_em"],
            },
        ),
    ]
