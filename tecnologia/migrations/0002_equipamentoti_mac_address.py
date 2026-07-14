from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tecnologia", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="equipamentoti",
            name="mac_address",
            field=models.CharField(blank=True, default="", max_length=17, verbose_name="MAC"),
        ),
    ]
