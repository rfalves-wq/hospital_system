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


def criar_ou_atualizar(model, codigo, nome, **extra):
    obj, _criado = model.objects.get_or_create(
        codigo=codigo,
        defaults={"nome": nome, **extra},
    )

    alterado = False
    if obj.nome != nome:
        obj.nome = nome
        alterado = True

    for campo, valor in extra.items():
        if getattr(obj, campo) != valor:
            setattr(obj, campo, valor)
            alterado = True

    if alterado:
        obj.save()

    return obj


def seed_catalogos(apps, schema_editor):
    Conselho = apps.get_model("cadastros", "ConselhoProfissional")
    Setor = apps.get_model("cadastros", "SetorHospitalar")
    Cargo = apps.get_model("cadastros", "CargoProfissional")
    Funcao = apps.get_model("cadastros", "FuncaoProfissional")
    Vinculo = apps.get_model("cadastros", "TipoVinculoTrabalho")

    conselhos = {
        "CRM": "CRM",
        "COREN": "COREN",
        "CRF": "CRF",
        "CRBM": "CRBM",
        "CRN": "CRN",
        "CRTR": "CRTR",
        "CREFITO": "CREFITO",
        "OUTRO": "Outro",
    }
    conselhos_obj = {
        codigo: criar_ou_atualizar(Conselho, codigo, nome)
        for codigo, nome in conselhos.items()
    }

    setores = [
        ("Acolhimento", "ASSISTENCIAL"),
        ("Recepcao", "ADMINISTRATIVO"),
        ("Classificacao", "ASSISTENCIAL"),
        ("Medico", "ASSISTENCIAL"),
        ("Medicacao", "ASSISTENCIAL"),
        ("Farmacia", "ESTOQUE"),
        ("Laboratorio", "ASSISTENCIAL"),
        ("Imagem", "ASSISTENCIAL"),
        ("Internacao", "ASSISTENCIAL"),
        ("Prontuario", "ADMINISTRATIVO"),
        ("Ambulancia", "APOIO"),
        ("TI", "APOIO"),
        ("Administrativo", "ADMINISTRATIVO"),
        ("RH", "ADMINISTRATIVO"),
        ("Manutencao", "APOIO"),
        ("Almoxarifado", "ESTOQUE"),
        ("Higienizacao", "APOIO"),
        ("Ouvidoria", "ADMINISTRATIVO"),
        ("SAC", "ADMINISTRATIVO"),
        ("Relatorios", "ADMINISTRATIVO"),
        ("Faturamento", "ADMINISTRATIVO"),
        ("Funcionarios", "ADMINISTRATIVO"),
        ("Estoque de Nutricao", "ESTOQUE"),
        ("Outro", "OUTRO"),
    ]
    setores_obj = {}
    for nome, tipo in setores:
        codigo = normalizar_codigo(nome)
        setores_obj[nome] = criar_ou_atualizar(Setor, codigo, nome, tipo=tipo)

    cargos = [
        ("Medico", "CRM", "Medico"),
        ("Enfermeiro", "COREN", "Medicacao"),
        ("Tecnico de enfermagem", "COREN", "Medicacao"),
        ("Auxiliar de enfermagem", "COREN", "Medicacao"),
        ("Classificador de risco", "COREN", "Classificacao"),
        ("Profissional do acolhimento", "COREN", "Acolhimento"),
        ("Farmaceutico", "CRF", "Farmacia"),
        ("Auxiliar de farmacia", "", "Farmacia"),
        ("Tecnico de laboratorio", "CRBM", "Laboratorio"),
        ("Biomedico", "CRBM", "Laboratorio"),
        ("Tecnico de radiologia", "CRTR", "Imagem"),
        ("Nutricionista", "CRN", "Estoque de Nutricao"),
        ("Fisioterapeuta", "CREFITO", "Internacao"),
        ("Recepcionista", "", "Recepcao"),
        ("Faturamento", "", "Faturamento"),
        ("Internacao", "", "Internacao"),
        ("Prontuario", "", "Prontuario"),
        ("Tecnologia da Informacao", "", "TI"),
        ("Suporte TI", "", "TI"),
        ("Motorista de ambulancia", "", "Ambulancia"),
        ("Transporte sanitario", "", "Ambulancia"),
        ("Regulacao", "", "Ambulancia"),
        ("Coordenador", "", "Administrativo"),
        ("Administrador do sistema", "", "Administrativo"),
    ]

    for nome, conselho_codigo, setor_nome in cargos:
        conselho = conselhos_obj.get(conselho_codigo) if conselho_codigo else None
        setor = setores_obj.get(setor_nome)
        cargo = criar_ou_atualizar(
            Cargo,
            normalizar_codigo(nome),
            nome,
            conselho_padrao=conselho,
        )
        criar_ou_atualizar(
            Funcao,
            normalizar_codigo(nome),
            nome,
            cargo=cargo,
            setor_padrao=setor,
        )

    for codigo, nome in [
        ("CLT", "CLT"),
        ("CONTRATO", "Contrato"),
        ("RPA", "RPA"),
        ("ESTAGIO", "Estagio"),
        ("TERCEIRIZADO", "Terceirizado"),
        ("OUTRO", "Outro"),
    ]:
        criar_ou_atualizar(Vinculo, codigo, nome)


class Migration(migrations.Migration):
    dependencies = [
        ("cadastros", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_catalogos, migrations.RunPython.noop),
    ]
