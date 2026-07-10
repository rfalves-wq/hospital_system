from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acolhimento', '0014_acolhimento_hora_chegada'),
    ]

    operations = [
        migrations.AddField(
            model_name='acolhimento',
            name='ausente_classificacao',
            field=models.BooleanField(default=False, verbose_name='Ausente na classificação'),
        ),
        migrations.AddField(
            model_name='acolhimento',
            name='chamadas_classificacao',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Chamadas na classificação'),
        ),
        migrations.AddField(
            model_name='acolhimento',
            name='data_ausente_classificacao',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Data da ausência na classificação'),
        ),
        migrations.AddField(
            model_name='acolhimento',
            name='data_ultima_chamada_classificacao',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Última chamada na classificação'),
        ),
    ]
