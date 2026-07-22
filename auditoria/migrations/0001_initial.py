import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EventoAuditoria",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("usuario_login", models.CharField(blank=True, db_index=True, default="", max_length=150)),
                ("profissional", models.CharField(blank=True, db_index=True, default="", max_length=180)),
                ("conselho", models.CharField(blank=True, default="", max_length=20)),
                ("registro", models.CharField(blank=True, default="", max_length=60)),
                (
                    "acao",
                    models.CharField(
                        choices=[
                            ("LOGIN", "Login"),
                            ("FALHA_LOGIN", "Falha de login"),
                            ("LOGOUT", "Logout"),
                            ("GRAVACAO", "Gravacao"),
                            ("STATUS", "Alteracao de status"),
                            ("IMPRESSAO", "Impressao"),
                            ("REENVIO", "Reenvio"),
                            ("ASSUMIR", "Assumir atendimento"),
                            ("ACESSO_NEGADO", "Acesso negado"),
                            ("ERRO", "Erro"),
                        ],
                        db_index=True,
                        max_length=30,
                    ),
                ),
                ("modulo", models.CharField(blank=True, db_index=True, default="", max_length=80)),
                ("descricao", models.CharField(blank=True, default="", max_length=255)),
                ("caminho", models.CharField(blank=True, default="", max_length=255)),
                ("metodo", models.CharField(blank=True, default="", max_length=10)),
                ("status_code", models.PositiveSmallIntegerField(blank=True, db_index=True, null=True)),
                ("ip", models.GenericIPAddressField(blank=True, null=True)),
                ("navegador", models.TextField(blank=True, default="")),
                ("objeto_tipo", models.CharField(blank=True, default="", max_length=80)),
                ("objeto_id", models.CharField(blank=True, db_index=True, default="", max_length=40)),
                ("numero_bam", models.CharField(blank=True, db_index=True, default="", max_length=30)),
                ("nome_paciente", models.CharField(blank=True, db_index=True, default="", max_length=200)),
                ("dados", models.JSONField(blank=True, default=dict)),
                ("criado_em", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "usuario",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="eventos_auditoria",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Evento de auditoria",
                "verbose_name_plural": "Eventos de auditoria",
                "ordering": ["-criado_em"],
            },
        ),
        migrations.AddIndex(
            model_name="eventoauditoria",
            index=models.Index(fields=["criado_em", "acao"], name="aud_dt_acao_idx"),
        ),
        migrations.AddIndex(
            model_name="eventoauditoria",
            index=models.Index(fields=["modulo", "criado_em"], name="aud_mod_dt_idx"),
        ),
        migrations.AddIndex(
            model_name="eventoauditoria",
            index=models.Index(fields=["usuario_login", "criado_em"], name="aud_user_dt_idx"),
        ),
        migrations.AddIndex(
            model_name="eventoauditoria",
            index=models.Index(fields=["numero_bam", "criado_em"], name="aud_bam_dt_idx"),
        ),
    ]
