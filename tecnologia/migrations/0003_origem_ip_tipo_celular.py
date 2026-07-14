from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tecnologia", "0002_equipamentoti_mac_address"),
    ]

    operations = [
        migrations.AlterField(
            model_name="equipamentoti",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("COMPUTADOR", "Computador"),
                    ("CELULAR", "Celular/Tablet"),
                    ("IMPRESSORA", "Impressora"),
                    ("SERVIDOR", "Servidor"),
                    ("REDE", "Rede"),
                    ("OUTRO", "Outro"),
                ],
                default="COMPUTADOR",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="equipamentoti",
            name="origem_ip",
            field=models.CharField(
                choices=[
                    ("DESCONHECIDO", "Nao identificado"),
                    ("DHCP", "DHCP"),
                    ("FIXO", "Fixo"),
                ],
                default="DESCONHECIDO",
                max_length=20,
                verbose_name="Origem do IP",
            ),
        ),
    ]
