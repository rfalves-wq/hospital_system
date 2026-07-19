from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ambulancia", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="solicitacaoambulancia",
            name="checklist_saida",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="solicitacaoambulancia",
            name="combustivel_chegada",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "---------"),
                    ("RESERVA", "Reserva"),
                    ("1/4", "1/4"),
                    ("1/2", "1/2"),
                    ("3/4", "3/4"),
                    ("CHEIO", "Cheio"),
                ],
                default="",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="solicitacaoambulancia",
            name="combustivel_saida",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "---------"),
                    ("RESERVA", "Reserva"),
                    ("1/4", "1/4"),
                    ("1/2", "1/2"),
                    ("3/4", "3/4"),
                    ("CHEIO", "Cheio"),
                ],
                default="",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="solicitacaoambulancia",
            name="condicao_paciente_chegada",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="solicitacaoambulancia",
            name="condicao_paciente_saida",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="solicitacaoambulancia",
            name="enfermeiro_transporte",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AddField(
            model_name="solicitacaoambulancia",
            name="equipamentos_medicos",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="solicitacaoambulancia",
            name="km_chegada",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="solicitacaoambulancia",
            name="km_saida",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="solicitacaoambulancia",
            name="medico_transporte",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AddField(
            model_name="solicitacaoambulancia",
            name="ocorrencias_transporte",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="solicitacaoambulancia",
            name="recebedor_destino",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AddField(
            model_name="solicitacaoambulancia",
            name="tecnico_transporte",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AlterField(
            model_name="solicitacaoambulancia",
            name="status",
            field=models.CharField(
                choices=[
                    ("SOLICITADO", "Solicitado"),
                    ("PREPARANDO", "Em preparo"),
                    ("AGUARDANDO_TRANSPORTE", "Aguardando transporte"),
                    ("SAIU", "Saiu com paciente"),
                    ("CONCLUIDO", "Chegou / concluido"),
                    ("CANCELADO", "Cancelado"),
                ],
                db_index=True,
                default="SOLICITADO",
                max_length=30,
            ),
        ),
    ]
