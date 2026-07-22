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


def seed_leitos(apps, schema_editor):
    Setor = apps.get_model("internacao", "SetorInternacao")
    Leito = apps.get_model("internacao", "LeitoInternacao")

    grupos = [
        ("Clinica medica", "CLINICO", [f"CM-{numero:02d}" for numero in range(1, 13)]),
        ("Observacao", "OBSERVACAO", [f"OBS-{numero:02d}" for numero in range(1, 9)]),
        ("Isolamento", "ISOLAMENTO", [f"ISO-{numero:02d}" for numero in range(1, 5)]),
    ]

    for ordem_setor, (setor_nome, tipo, codigos) in enumerate(grupos, start=1):
        setor, _criado = Setor.objects.get_or_create(
            nome=setor_nome,
            defaults={
                "codigo": normalizar_codigo(setor_nome),
                "ordem": ordem_setor,
            },
        )

        for ordem_leito, codigo in enumerate(codigos, start=1):
            Leito.objects.get_or_create(
                setor=setor,
                codigo=codigo,
                defaults={
                    "tipo": tipo,
                    "ordem": ordem_leito,
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ("internacao", "0003_leitointernacao_setorinternacao_internacao_leito_ref_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_leitos, migrations.RunPython.noop),
    ]
