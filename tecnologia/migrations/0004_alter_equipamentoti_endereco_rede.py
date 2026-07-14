from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tecnologia", "0003_origem_ip_tipo_celular"),
    ]

    operations = [
        migrations.AlterField(
            model_name="equipamentoti",
            name="endereco_rede",
            field=models.CharField(
                help_text="Ex: 192.168.0.10 ou impressora-recepcao",
                max_length=180,
                verbose_name="IP ou nome da maquina",
            ),
        ),
    ]
