from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("acolhimento", "0022_acolhimento_trava_atendimento_medico"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SolicitacaoAmbulancia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero_bam", models.CharField(blank=True, db_index=True, default="", max_length=20)),
                ("nome_paciente", models.CharField(max_length=200)),
                ("cpf", models.CharField(blank=True, db_index=True, default="", max_length=14)),
                ("data_nascimento", models.DateField(blank=True, null=True)),
                ("idade", models.PositiveIntegerField(blank=True, null=True)),
                ("tipo_transporte", models.CharField(choices=[("TRANSFERENCIA", "Transferencia"), ("EXAME_EXTERNO", "Exame externo"), ("ALTA", "Alta com transporte"), ("REMOCAO", "Remocao"), ("OUTRO", "Outro")], default="TRANSFERENCIA", max_length=30)),
                ("prioridade", models.CharField(choices=[("BAIXA", "Baixa"), ("NORMAL", "Normal"), ("URGENTE", "Urgente"), ("EMERGENCIA", "Emergencia")], default="NORMAL", max_length=20)),
                ("status", models.CharField(choices=[("SOLICITADO", "Solicitado"), ("PREPARANDO", "Em preparo"), ("AGUARDANDO_TRANSPORTE", "Aguardando transporte"), ("SAIU", "Saiu com paciente"), ("CONCLUIDO", "Concluido"), ("CANCELADO", "Cancelado")], db_index=True, default="SOLICITADO", max_length=30)),
                ("origem", models.CharField(blank=True, default="Hospital", max_length=160)),
                ("destino", models.CharField(max_length=220)),
                ("unidade_destino", models.CharField(blank=True, default="", max_length=180)),
                ("motivo", models.TextField()),
                ("resumo_clinico", models.TextField(blank=True, default="")),
                ("observacoes", models.TextField(blank=True, default="")),
                ("necessita_maca", models.BooleanField(default=True)),
                ("necessita_oxigenio", models.BooleanField(default=False)),
                ("necessita_isolamento", models.BooleanField(default=False)),
                ("acompanhante", models.BooleanField(default=False)),
                ("profissional_solicitante", models.CharField(blank=True, default="", max_length=150)),
                ("conselho_solicitante", models.CharField(blank=True, default="", max_length=20)),
                ("registro_solicitante", models.CharField(blank=True, default="", max_length=60)),
                ("setor_solicitante", models.CharField(blank=True, default="", max_length=120)),
                ("contato", models.CharField(blank=True, default="", max_length=120)),
                ("responsavel_transporte", models.CharField(blank=True, default="", max_length=150)),
                ("veiculo", models.CharField(blank=True, default="", max_length=120)),
                ("placa", models.CharField(blank=True, default="", max_length=20)),
                ("motorista", models.CharField(blank=True, default="", max_length=150)),
                ("solicitado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("preparo_em", models.DateTimeField(blank=True, null=True)),
                ("aguardando_transporte_em", models.DateTimeField(blank=True, null=True)),
                ("saida_em", models.DateTimeField(blank=True, null=True)),
                ("concluido_em", models.DateTimeField(blank=True, null=True)),
                ("cancelado_em", models.DateTimeField(blank=True, null=True)),
                ("status_atualizado_por", models.CharField(blank=True, default="", max_length=150)),
                ("acolhimento", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="solicitacoes_ambulancia", to="acolhimento.acolhimento")),
                ("solicitante", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="solicitacoes_ambulancia", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Solicitacao de ambulancia",
                "verbose_name_plural": "Solicitacoes de ambulancia",
                "ordering": ["-solicitado_em"],
            },
        ),
        migrations.AddIndex(
            model_name="solicitacaoambulancia",
            index=models.Index(fields=["status", "solicitado_em"], name="amb_status_dt_idx"),
        ),
        migrations.AddIndex(
            model_name="solicitacaoambulancia",
            index=models.Index(fields=["numero_bam", "solicitado_em"], name="amb_bam_dt_idx"),
        ),
        migrations.AddIndex(
            model_name="solicitacaoambulancia",
            index=models.Index(fields=["prioridade", "status"], name="amb_prior_status_idx"),
        ),
    ]
