from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="EquipamentoTI",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID"
                    )
                ),
                ("nome", models.CharField(max_length=120)),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("COMPUTADOR", "Computador"),
                            ("IMPRESSORA", "Impressora"),
                            ("SERVIDOR", "Servidor"),
                            ("REDE", "Rede"),
                            ("OUTRO", "Outro"),
                        ],
                        default="COMPUTADOR",
                        max_length=20,
                    )
                ),
                ("setor", models.CharField(blank=True, default="", max_length=120)),
                (
                    "endereco_rede",
                    models.CharField(
                        help_text="Ex: 192.168.0.10 ou impressora-recepcao",
                        max_length=180,
                        verbose_name="IP ou host",
                    )
                ),
                ("ativo", models.BooleanField(default=True)),
                (
                    "ultimo_status",
                    models.CharField(
                        choices=[
                            ("ONLINE", "Online"),
                            ("OFFLINE", "Offline"),
                            ("DESCONHECIDO", "Nao verificado"),
                        ],
                        default="DESCONHECIDO",
                        max_length=20,
                    )
                ),
                ("ultimo_tempo_ms", models.PositiveIntegerField(blank=True, null=True)),
                ("ultima_verificacao", models.DateTimeField(blank=True, null=True)),
                ("observacao", models.TextField(blank=True, default="")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Equipamento de TI",
                "verbose_name_plural": "Equipamentos de TI",
                "ordering": ["nome"],
            },
        ),
    ]
