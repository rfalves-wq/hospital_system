from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_perfis_paineis_acesso"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="conselho_profissional",
            field=models.CharField(
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
                max_length=20,
                verbose_name="Conselho profissional",
            ),
        ),
        migrations.AddField(
            model_name="usuario",
            name="registro_profissional",
            field=models.CharField(
                blank=True,
                max_length=40,
                verbose_name="Registro profissional",
            ),
        ),
    ]
