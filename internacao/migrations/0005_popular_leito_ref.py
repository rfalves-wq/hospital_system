from django.db import migrations


def normalizar_codigo(valor, tamanho=40):
    mapa = str.maketrans(
        "áàãâäéèêëíìîïóòõôöúùûüçÁÀÃÂÄÉÈÊËÍÌÎÏÓÒÕÔÖÚÙÛÜÇ",
        "aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC",
    )
    codigo = (valor or "").translate(mapa).upper()
    codigo = "".join(char if char.isalnum() else "_" for char in codigo)
    codigo = "_".join(parte for parte in codigo.split("_") if parte)
    return (codigo or "SEM_CODIGO")[:tamanho]


def popular_leitos(apps, schema_editor):
    Internacao = apps.get_model("internacao", "Internacao")
    Setor = apps.get_model("internacao", "SetorInternacao")
    Leito = apps.get_model("internacao", "LeitoInternacao")

    for internacao in Internacao.objects.exclude(leito="").filter(leito_ref__isnull=True):
        setor_nome = (internacao.setor or "Internacao").strip()
        setor, _criado = Setor.objects.get_or_create(
            nome=setor_nome,
            defaults={"codigo": normalizar_codigo(setor_nome), "ordem": 999},
        )
        leito, _criado = Leito.objects.get_or_create(
            setor=setor,
            codigo=internacao.leito.strip(),
            defaults={"ordem": 999},
        )
        internacao.leito_ref_id = leito.id
        internacao.save(update_fields=["leito_ref"])


class Migration(migrations.Migration):
    dependencies = [
        ("internacao", "0004_seed_leitos_base"),
    ]

    operations = [
        migrations.RunPython(popular_leitos, migrations.RunPython.noop),
    ]
