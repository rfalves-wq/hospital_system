from datetime import datetime

from django.db import migrations
from django.utils import timezone


STATUS_PARA_SETOR = {
    "RECEPCAO": "RECEPCAO",
    "CLASSIFICACAO": "CLASSIFICACAO",
    "CONSULTA": "MEDICO",
    "RETORNO_MEDICO": "MEDICO",
    "PROCEDIMENTOS": "PROCEDIMENTOS",
    "OBSERVACAO": "OBSERVACAO",
    "INTERNACAO": "INTERNACAO",
    "AUSENTE": "AUSENTE",
}


def data_hora_chegada(acolhimento):
    data_base = acolhimento.data_acolhimento or timezone.now()

    if timezone.is_aware(data_base):
        data_local = timezone.localtime(data_base)
    else:
        data_local = data_base

    if not acolhimento.hora_chegada:
        return data_base

    chegada = datetime.combine(data_local.date(), acolhimento.hora_chegada)

    if timezone.is_aware(data_base):
        chegada = timezone.make_aware(chegada, timezone.get_current_timezone())

    if chegada > data_base:
        return data_base

    return chegada


def criar_permanencias_iniciais(apps, schema_editor):
    Acolhimento = apps.get_model("acolhimento", "Acolhimento")
    Permanencia = apps.get_model("acolhimento", "PermanenciaSetorAtendimento")

    for acolhimento in Acolhimento.objects.all().iterator():
        if Permanencia.objects.filter(acolhimento_id=acolhimento.id).exists():
            continue

        data_acolhimento = acolhimento.data_acolhimento or timezone.now()

        Permanencia.objects.create(
            acolhimento_id=acolhimento.id,
            setor="ACOLHIMENTO",
            status_origem="ACOLHIMENTO",
            origem="STATUS",
            entrada=data_hora_chegada(acolhimento),
            saida=data_acolhimento,
            observacao="Registro inicial criado na ativacao do controle de tempo.",
        )

        setor_atual = STATUS_PARA_SETOR.get(acolhimento.status)

        if setor_atual:
            Permanencia.objects.create(
                acolhimento_id=acolhimento.id,
                setor=setor_atual,
                status_origem=acolhimento.status or "",
                origem="STATUS",
                entrada=data_acolhimento,
                saida=None,
                observacao="Setor atual aberto na ativacao do controle de tempo.",
            )


class Migration(migrations.Migration):

    dependencies = [
        ("acolhimento", "0020_permanencia_setor_atendimento"),
    ]

    operations = [
        migrations.RunPython(criar_permanencias_iniciais, migrations.RunPython.noop),
    ]
