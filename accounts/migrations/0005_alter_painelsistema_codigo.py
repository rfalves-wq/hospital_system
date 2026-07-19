from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_painel_ambulancia"),
    ]

    operations = [
        migrations.AlterField(
            model_name="painelsistema",
            name="codigo",
            field=models.CharField(
                choices=[
                    ("acolhimento", "Acolhimento"),
                    ("recepcao", "Recepcao"),
                    ("classificacao", "Classificacao de risco"),
                    ("medico", "Medico"),
                    ("prontuario", "Prontuario"),
                    ("medicacao", "Sala de medicacao"),
                    ("farmacia", "Farmacia"),
                    ("internacao", "Internacao"),
                    ("laboratorio", "Laboratorio"),
                    ("imagem", "Imagem"),
                    ("ti", "Tecnologia da Informacao"),
                    ("suporte_ti", "Solicitar TI"),
                    ("painel_chamados", "Painel de chamados"),
                    ("ambulancia", "Solicitacao de Ambulancia"),
                ],
                max_length=40,
                unique=True,
                verbose_name="Painel",
            ),
        ),
    ]
