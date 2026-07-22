from django.db import migrations


def normalizar_codigo(valor, tamanho=50):
    mapa = str.maketrans(
        "áàãâäéèêëíìîïóòõôöúùûüçÁÀÃÂÄÉÈÊËÍÌÎÏÓÒÕÔÖÚÙÛÜÇ",
        "aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC",
    )
    codigo = (valor or "").translate(mapa).upper()
    codigo = "".join(char if char.isalnum() else "_" for char in codigo)
    codigo = "_".join(parte for parte in codigo.split("_") if parte)
    return (codigo or "SEM_CODIGO")[:tamanho]


def resolver(model, valor):
    valor = (valor or "").strip()
    if not valor:
        return None

    codigo = normalizar_codigo(valor)
    return (
        model.objects.filter(codigo=codigo).first()
        or model.objects.filter(nome__iexact=valor).first()
    )


def popular_referencias(apps, schema_editor):
    Usuario = apps.get_model("accounts", "Usuario")
    Cargo = apps.get_model("cadastros", "CargoProfissional")
    Funcao = apps.get_model("cadastros", "FuncaoProfissional")
    Conselho = apps.get_model("cadastros", "ConselhoProfissional")

    for usuario in Usuario.objects.all().iterator():
        alterado = False

        if usuario.cargo and not usuario.cargo_ref_id:
            cargo = resolver(Cargo, usuario.cargo)
            if cargo:
                usuario.cargo_ref_id = cargo.id
                alterado = True

        if usuario.cargo and not usuario.funcao_ref_id:
            funcao = resolver(Funcao, usuario.cargo)
            if funcao:
                usuario.funcao_ref_id = funcao.id
                alterado = True

        if usuario.conselho_profissional and not usuario.conselho_ref_id:
            conselho = resolver(Conselho, usuario.conselho_profissional)
            if conselho:
                usuario.conselho_ref_id = conselho.id
                alterado = True

        if alterado:
            usuario.save(update_fields=["cargo_ref", "funcao_ref", "conselho_ref"])


class Migration(migrations.Migration):
    dependencies = [
        ("cadastros", "0002_seed_catalogos_base"),
        ("accounts", "0011_usuario_cargo_ref_usuario_conselho_ref_and_more"),
    ]

    operations = [
        migrations.RunPython(popular_referencias, migrations.RunPython.noop),
    ]
