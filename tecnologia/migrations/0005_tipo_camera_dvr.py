from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tecnologia", "0004_alter_equipamentoti_endereco_rede"),
    ]

    operations = [
        migrations.AlterField(
            model_name="equipamentoti",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("COMPUTADOR", "Computador"),
                    ("CELULAR", "Celular/Tablet"),
                    ("CAMERA", "Camera"),
                    ("DVR", "DVR/NVR"),
                    ("IMPRESSORA", "Impressora"),
                    ("SERVIDOR", "Servidor"),
                    ("REDE", "Rede"),
                    ("OUTRO", "Outro"),
                ],
                default="COMPUTADOR",
                max_length=20,
            ),
        ),
    ]
