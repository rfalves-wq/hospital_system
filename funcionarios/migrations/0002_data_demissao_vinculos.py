import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("funcionarios", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="funcionario",
            name="data_demissao",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="VinculoFuncionario",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data_admissao", models.DateField(db_index=True)),
                ("data_demissao", models.DateField(blank=True, db_index=True, null=True)),
                (
                    "tipo_vinculo",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "---------"),
                            ("CLT", "CLT"),
                            ("CONTRATO", "Contrato"),
                            ("RPA", "RPA"),
                            ("ESTAGIO", "Estagio"),
                            ("TERCEIRIZADO", "Terceirizado"),
                            ("OUTRO", "Outro"),
                        ],
                        default="",
                        max_length=20,
                    ),
                ),
                ("cargo", models.CharField(blank=True, default="", max_length=100)),
                (
                    "setor",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "---------"),
                            ("Acolhimento", "Acolhimento"),
                            ("Recepcao", "Recepcao"),
                            ("Classificacao", "Classificacao"),
                            ("Medico", "Medico"),
                            ("Medicacao", "Medicacao"),
                            ("Farmacia", "Farmacia"),
                            ("Laboratorio", "Laboratorio"),
                            ("Imagem", "Imagem"),
                            ("Internacao", "Internacao"),
                            ("Prontuario", "Prontuario"),
                            ("Ambulancia", "Ambulancia"),
                            ("TI", "TI"),
                            ("Administrativo", "Administrativo"),
                            ("RH", "RH"),
                            ("Manutencao", "Manutencao"),
                            ("Almoxarifado", "Almoxarifado"),
                            ("Outro", "Outro"),
                        ],
                        default="",
                        max_length=80,
                    ),
                ),
                ("motivo_demissao", models.CharField(blank=True, default="", max_length=180)),
                ("observacoes", models.TextField(blank=True, default="")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                (
                    "funcionario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vinculos",
                        to="funcionarios.funcionario",
                    ),
                ),
                (
                    "unidade",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="vinculos_funcionarios",
                        to="unidades.unidademedica",
                    ),
                ),
            ],
            options={
                "verbose_name": "Vinculo do funcionario",
                "verbose_name_plural": "Vinculos dos funcionarios",
                "ordering": ["-data_admissao", "-id"],
            },
        ),
        migrations.AddIndex(
            model_name="vinculofuncionario",
            index=models.Index(fields=["funcionario", "data_admissao"], name="vinc_func_adm_idx"),
        ),
        migrations.AddIndex(
            model_name="vinculofuncionario",
            index=models.Index(fields=["data_demissao", "funcionario"], name="vinc_dem_func_idx"),
        ),
    ]
