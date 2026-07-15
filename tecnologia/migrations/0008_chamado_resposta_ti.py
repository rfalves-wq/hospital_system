from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tecnologia", "0007_chamado_servico_usuario"),
    ]

    operations = [
        migrations.AddField(
            model_name="chamadomanutencaoti",
            name="respondido_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="chamadomanutencaoti",
            name="respondido_por",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="chamadomanutencaoti",
            name="resposta_ti",
            field=models.TextField(blank=True, default="", verbose_name="Resposta do TI"),
        ),
    ]
