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


def popular_funcionario(funcionario, Cargo, Funcao, Conselho, Setor, Vinculo):
    alterado = False

    if funcionario.cargo and not funcionario.cargo_ref_id:
        cargo = resolver(Cargo, funcionario.cargo)
        if cargo:
            funcionario.cargo_ref_id = cargo.id
            alterado = True

    if funcionario.funcao and not funcionario.funcao_ref_id:
        funcao = resolver(Funcao, funcionario.funcao)
        if funcao:
            funcionario.funcao_ref_id = funcao.id
            alterado = True
    elif funcionario.cargo and not funcionario.funcao_ref_id:
        funcao = resolver(Funcao, funcionario.cargo)
        if funcao:
            funcionario.funcao_ref_id = funcao.id
            alterado = True

    if funcionario.conselho_profissional and not funcionario.conselho_ref_id:
        conselho = resolver(Conselho, funcionario.conselho_profissional)
        if conselho:
            funcionario.conselho_ref_id = conselho.id
            alterado = True

    if funcionario.setor and not funcionario.setor_ref_id:
        setor = resolver(Setor, funcionario.setor)
        if setor:
            funcionario.setor_ref_id = setor.id
            alterado = True

    if funcionario.tipo_vinculo and not funcionario.tipo_vinculo_ref_id:
        tipo = resolver(Vinculo, funcionario.tipo_vinculo)
        if tipo:
            funcionario.tipo_vinculo_ref_id = tipo.id
            alterado = True

    if alterado:
        funcionario.save(
            update_fields=[
                "cargo_ref",
                "funcao_ref",
                "conselho_ref",
                "setor_ref",
                "tipo_vinculo_ref",
            ]
        )


def popular_referencias(apps, schema_editor):
    Funcionario = apps.get_model("funcionarios", "Funcionario")
    EscalaFuncionario = apps.get_model("funcionarios", "EscalaFuncionario")
    VinculoFuncionario = apps.get_model("funcionarios", "VinculoFuncionario")
    Cargo = apps.get_model("cadastros", "CargoProfissional")
    Funcao = apps.get_model("cadastros", "FuncaoProfissional")
    Conselho = apps.get_model("cadastros", "ConselhoProfissional")
    Setor = apps.get_model("cadastros", "SetorHospitalar")
    Vinculo = apps.get_model("cadastros", "TipoVinculoTrabalho")

    for funcionario in Funcionario.objects.all().iterator():
        popular_funcionario(funcionario, Cargo, Funcao, Conselho, Setor, Vinculo)

    for escala in EscalaFuncionario.objects.exclude(setor="").filter(setor_ref__isnull=True):
        setor = resolver(Setor, escala.setor)
        if setor:
            escala.setor_ref_id = setor.id
            escala.save(update_fields=["setor_ref"])

    for vinculo in VinculoFuncionario.objects.all().iterator():
        alterado = False

        if vinculo.cargo and not vinculo.cargo_ref_id:
            cargo = resolver(Cargo, vinculo.cargo)
            if cargo:
                vinculo.cargo_ref_id = cargo.id
                alterado = True

        if vinculo.setor and not vinculo.setor_ref_id:
            setor = resolver(Setor, vinculo.setor)
            if setor:
                vinculo.setor_ref_id = setor.id
                alterado = True

        if vinculo.tipo_vinculo and not vinculo.tipo_vinculo_ref_id:
            tipo = resolver(Vinculo, vinculo.tipo_vinculo)
            if tipo:
                vinculo.tipo_vinculo_ref_id = tipo.id
                alterado = True

        if alterado:
            vinculo.save(update_fields=["cargo_ref", "setor_ref", "tipo_vinculo_ref"])


class Migration(migrations.Migration):
    dependencies = [
        ("cadastros", "0002_seed_catalogos_base"),
        ("funcionarios", "0003_escalafuncionario_setor_ref_funcionario_cargo_ref_and_more"),
    ]

    operations = [
        migrations.RunPython(popular_referencias, migrations.RunPython.noop),
    ]
