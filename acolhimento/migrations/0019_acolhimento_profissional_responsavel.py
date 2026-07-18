from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("acolhimento", "0018_acolhimento_acolh_status_data_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="acolhimento",
            name="profissional_responsavel",
            field=models.CharField(
                blank=True,
                default="",
                max_length=150,
                verbose_name="Profissional responsavel",
            ),
        ),
        migrations.AddField(
            model_name="acolhimento",
            name="profissional_responsavel_conselho",
            field=models.CharField(
                blank=True,
                default="",
                max_length=20,
                verbose_name="Conselho profissional",
            ),
        ),
        migrations.AddField(
            model_name="acolhimento",
            name="profissional_responsavel_registro",
            field=models.CharField(
                blank=True,
                default="",
                max_length=40,
                verbose_name="Registro profissional",
            ),
        ),
    ]
