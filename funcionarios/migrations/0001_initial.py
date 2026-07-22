import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("unidades", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Funcionario",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(db_index=True, max_length=180)),
                ("cpf", models.CharField(blank=True, db_index=True, default="", max_length=14)),
                ("matricula", models.CharField(blank=True, db_index=True, default="", max_length=40)),
                ("cargo", models.CharField(blank=True, db_index=True, default="", max_length=100)),
                ("funcao", models.CharField(blank=True, default="", max_length=120)),
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
                        db_index=True,
                        default="",
                        max_length=80,
                    ),
                ),
                (
                    "conselho_profissional",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "---------"),
                            ("CRM", "CRM"),
                            ("COREN", "COREN"),
                            ("CRF", "CRF"),
                            ("CRBM", "CRBM"),
                            ("CRN", "CRN"),
                            ("CRTR", "CRTR"),
                            ("CREFITO", "CREFITO"),
                            ("OUTRO", "Outro"),
                        ],
                        default="",
                        max_length=20,
                    ),
                ),
                ("registro_profissional", models.CharField(blank=True, default="", max_length=40)),
                ("telefone", models.CharField(blank=True, default="", max_length=30)),
                ("email", models.EmailField(blank=True, default="", max_length=254)),
                ("data_admissao", models.DateField(blank=True, null=True)),
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
                ("carga_horaria_semanal", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("ativo", models.BooleanField(db_index=True, default=True)),
                ("observacoes", models.TextField(blank=True, default="")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                (
                    "unidade",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="funcionarios",
                        to="unidades.unidademedica",
                    ),
                ),
                (
                    "usuario",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="cadastro_funcionario",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Funcionario",
                "verbose_name_plural": "Funcionarios",
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="EscalaFuncionario",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", models.DateField(db_index=True)),
                (
                    "turno",
                    models.CharField(
                        choices=[
                            ("MANHA", "Manha"),
                            ("TARDE", "Tarde"),
                            ("NOITE", "Noite"),
                            ("PLANTAO_12H", "Plantao 12h"),
                            ("PLANTAO_24H", "Plantao 24h"),
                            ("OUTRO", "Outro"),
                        ],
                        default="MANHA",
                        max_length=20,
                    ),
                ),
                ("hora_inicio", models.TimeField(blank=True, null=True)),
                ("hora_fim", models.TimeField(blank=True, null=True)),
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
                        db_index=True,
                        default="",
                        max_length=80,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PREVISTA", "Prevista"),
                            ("CONFIRMADA", "Confirmada"),
                            ("FALTA", "Falta"),
                            ("TROCA", "Troca"),
                            ("CANCELADA", "Cancelada"),
                        ],
                        db_index=True,
                        default="PREVISTA",
                        max_length=20,
                    ),
                ),
                ("observacoes", models.CharField(blank=True, default="", max_length=255)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                (
                    "funcionario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="escalas",
                        to="funcionarios.funcionario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Escala de funcionario",
                "verbose_name_plural": "Escalas de funcionarios",
                "ordering": ["data", "hora_inicio", "funcionario__nome"],
            },
        ),
        migrations.AddIndex(
            model_name="funcionario",
            index=models.Index(fields=["ativo", "setor"], name="func_ativo_setor_idx"),
        ),
        migrations.AddIndex(
            model_name="funcionario",
            index=models.Index(fields=["cargo", "ativo"], name="func_cargo_ativo_idx"),
        ),
        migrations.AddIndex(
            model_name="escalafuncionario",
            index=models.Index(fields=["data", "setor"], name="escala_data_setor_idx"),
        ),
        migrations.AddIndex(
            model_name="escalafuncionario",
            index=models.Index(fields=["funcionario", "data"], name="escala_func_data_idx"),
        ),
    ]
