from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("painel", "0004_chamadapainel_chamada_setor_dt_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="chamadapainel",
            name="visivel_painel",
            field=models.BooleanField(default=True, verbose_name="Visivel no painel"),
        ),
    ]
