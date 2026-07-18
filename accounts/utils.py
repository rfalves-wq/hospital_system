CONSELHO_PADRAO_POR_CARGO = {
    "Medico": "CRM",
    "Enfermeiro": "COREN",
    "Tecnico de enfermagem": "COREN",
    "Auxiliar de enfermagem": "COREN",
    "Classificador de risco": "COREN",
    "Profissional do acolhimento": "COREN",
    "Farmaceutico": "CRF",
    "Tecnico de laboratorio": "CRBM",
    "Biomedico": "CRBM",
    "Tecnico de radiologia": "CRTR",
    "Nutricionista": "CRN",
}


def nome_profissional_usuario(user):
    if not user or not getattr(user, "is_authenticated", False):
        return ""

    return user.get_full_name() or user.username


def nome_profissional_request(request):
    return nome_profissional_usuario(getattr(request, "user", None))


def conselho_profissional_usuario(user):
    if not user or not getattr(user, "is_authenticated", False):
        return ""

    conselho = getattr(user, "conselho_profissional", "") or ""
    cargo = getattr(user, "cargo", "") or ""

    return conselho or CONSELHO_PADRAO_POR_CARGO.get(cargo, "")


def registro_profissional_usuario(user):
    if not user or not getattr(user, "is_authenticated", False):
        return ""

    return getattr(user, "registro_profissional", "") or ""


def conselho_registro_profissional(conselho, registro):
    conselho = (conselho or "").strip()
    registro = (registro or "").strip()

    if conselho and registro:
        return f"{conselho} {registro}"

    return conselho or registro


def identificacao_conselho_usuario(user):
    return conselho_registro_profissional(
        conselho_profissional_usuario(user),
        registro_profissional_usuario(user),
    )


def conselho_profissional_request(request):
    return conselho_profissional_usuario(getattr(request, "user", None))


def registro_profissional_request(request):
    return registro_profissional_usuario(getattr(request, "user", None))


def identificacao_conselho_request(request):
    return identificacao_conselho_usuario(getattr(request, "user", None))
