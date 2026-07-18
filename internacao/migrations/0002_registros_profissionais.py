from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internacao", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="internacao",
            name="profissional_responsavel_registro",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="internacao",
            name="profissional_alta_registro",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="evolucaointernacao",
            name="profissional_registro",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
    ]
