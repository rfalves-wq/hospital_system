from django.db import migrations


def popular_equipe(apps, solicitacao):
    Membro = apps.get_model("ambulancia", "MembroEquipeAmbulancia")
    dados = [
        ("RESPONSAVEL", solicitacao.responsavel_transporte, 1),
        ("MOTORISTA", solicitacao.motorista, 2),
        ("MEDICO", solicitacao.medico_transporte, 3),
        ("ENFERMEIRO", solicitacao.enfermeiro_transporte, 4),
        ("TECNICO", solicitacao.tecnico_transporte, 5),
    ]

    for papel, nome, ordem in dados:
        nome = (nome or "").strip()
        if not nome:
            continue

        Membro.objects.update_or_create(
            solicitacao=solicitacao,
            papel=papel,
            nome=nome,
            defaults={"ordem": ordem},
        )


def popular_equipamentos(apps, solicitacao):
    import re

    Equipamento = apps.get_model("ambulancia", "EquipamentoMedicoAmbulancia")
    Item = apps.get_model("ambulancia", "EquipamentoSolicitacaoAmbulancia")
    texto = solicitacao.equipamentos_medicos or ""
    itens = [
        item.strip()
        for item in re.split(r"[\n;,]+", texto)
        if item.strip()
    ]

    for item in itens:
        equipamento, _criado = Equipamento.objects.get_or_create(nome=item[:120])
        Item.objects.update_or_create(
            solicitacao=solicitacao,
            equipamento=equipamento,
            defaults={"quantidade": 1},
        )


def popular_relacionamentos(apps, schema_editor):
    Solicitacao = apps.get_model("ambulancia", "SolicitacaoAmbulancia")

    for solicitacao in Solicitacao.objects.all().iterator():
        popular_equipe(apps, solicitacao)
        popular_equipamentos(apps, solicitacao)


class Migration(migrations.Migration):
    dependencies = [
        ("ambulancia", "0003_equipamentomedicoambulancia_and_more"),
    ]

    operations = [
        migrations.RunPython(popular_relacionamentos, migrations.RunPython.noop),
    ]
