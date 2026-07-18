from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("classificacao", "0004_classificacaorisco_classif_data_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="classificacaorisco",
            name="responsavel_registro",
            field=models.CharField(
                blank=True,
                default="",
                max_length=50,
                verbose_name="COREN / registro do responsavel",
            ),
        ),
    ]
