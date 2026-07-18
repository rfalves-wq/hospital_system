from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("acolhimento", "0019_acolhimento_profissional_responsavel"),
    ]

    operations = [
        migrations.CreateModel(
            name="PermanenciaSetorAtendimento",
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
                            ("ACOLHIMENTO", "Acolhimento"),
                            ("RECEPCAO", "Recepcao"),
                            ("CLASSIFICACAO", "Classificacao de risco"),
                            ("MEDICO", "Medico"),
                            ("PROCEDIMENTOS", "Procedimentos"),
                            ("FARMACIA", "Farmacia"),
                            ("MEDICACAO", "Medicacao"),
                            ("LABORATORIO", "Laboratorio"),
                            ("IMAGEM", "Imagem"),
                            ("OBSERVACAO", "Observacao"),
                            ("INTERNACAO", "Internacao"),
                            ("AUSENTE", "Ausente"),
                        ],
                        max_length=30,
                    ),
                ),
                ("status_origem", models.CharField(blank=True, default="", max_length=20)),
                (
                    "origem",
                    models.CharField(
                        choices=[
                            ("STATUS", "Status do atendimento"),
                            ("PROCEDIMENTO", "Procedimento"),
                        ],
                        default="STATUS",
                        max_length=20,
                    ),
                ),
                ("entrada", models.DateTimeField()),
                ("saida", models.DateTimeField(blank=True, null=True)),
                ("observacao", models.CharField(blank=True, default="", max_length=255)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                (
                    "acolhimento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tempos_setores",
                        to="acolhimento.acolhimento",
                    ),
                ),
            ],
            options={
                "verbose_name": "Permanencia por setor",
                "verbose_name_plural": "Permanencias por setor",
                "ordering": ["entrada", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="permanenciasetoratendimento",
            index=models.Index(
                fields=["acolhimento", "setor", "saida"],
                name="perm_setor_aberto_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="permanenciasetoratendimento",
            index=models.Index(
                fields=["acolhimento", "entrada"],
                name="perm_acolh_entrada_idx",
            ),
        ),
    ]
