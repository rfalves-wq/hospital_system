from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tecnologia", "0006_chamadomanutencaoti"),
    ]

    operations = [
        migrations.AddField(
            model_name="chamadomanutencaoti",
            name="contato",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="chamadomanutencaoti",
            name="setor_solicitante",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="chamadomanutencaoti",
            name="tipo_servico",
            field=models.CharField(
                choices=[
                    ("SUPORTE", "Suporte"),
                    ("MANUTENCAO", "Manutencao"),
                    ("INSTALACAO", "Instalacao"),
                    ("REDE", "Rede/Internet"),
                    ("SISTEMA", "Sistema"),
                    ("OUTRO", "Outro"),
                ],
                default="SUPORTE",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="chamadomanutencaoti",
            name="equipamento",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="chamados_manutencao",
                to="tecnologia.equipamentoti",
            ),
        ),
        migrations.AlterModelOptions(
            name="chamadomanutencaoti",
            options={
                "ordering": ["-criado_em"],
                "verbose_name": "Pedido de servico de TI",
                "verbose_name_plural": "Pedidos de servico de TI",
            },
        ),
    ]
