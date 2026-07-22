from django.utils import timezone

from .models import ChamadaPainel


MAX_CHAMADAS_POR_SETOR = 4


def nome_paciente_acolhimento(acolhimento):
    if acolhimento.paciente:
        return acolhimento.paciente.nome_completo

    return acolhimento.nome_paciente


def nome_usuario(request):
    if request and request.user.is_authenticated:
        return request.user.get_full_name() or request.user.username

    return ""


def total_chamadas_setor(setor, acolhimento):
    if not acolhimento or not acolhimento.pk:
        return 0

    chamadas = ChamadaPainel.objects.filter(
        setor=setor,
        acolhimento=acolhimento,
        tipo=ChamadaPainel.CHAMADA,
    )
    ultimo_marco = (
        ChamadaPainel.objects
        .filter(
            setor=setor,
            acolhimento=acolhimento,
            tipo__in=[ChamadaPainel.AUSENCIA, ChamadaPainel.RETORNO],
        )
        .order_by("-id")
        .first()
    )

    if ultimo_marco:
        chamadas = chamadas.filter(id__gt=ultimo_marco.id)

    return chamadas.count()


def anexar_status_chamadas(objetos, setor, attr_acolhimento=None):
    for objeto in objetos:
        acolhimento = (
            getattr(objeto, attr_acolhimento)
            if attr_acolhimento
            else objeto
        )
        total = total_chamadas_setor(setor, acolhimento)

        objeto.painel_chamadas = total
        objeto.painel_pode_chamar = total < MAX_CHAMADAS_POR_SETOR
        objeto.painel_pode_ausentar = total >= MAX_CHAMADAS_POR_SETOR

    return objetos


def registrar_chamada(
    setor,
    acolhimento,
    request=None,
    local_destino="",
    observacao="",
    tipo=ChamadaPainel.CHAMADA,
    visivel_painel=True,
):
    return ChamadaPainel.objects.create(
        tipo=tipo,
        setor=setor,
        acolhimento=acolhimento,
        numero_bam=acolhimento.numero_bam or "",
        paciente_nome=nome_paciente_acolhimento(acolhimento),
        local_destino=local_destino,
        observacao=observacao,
        visivel_painel=visivel_painel,
        chamado_por=request.user if request and request.user.is_authenticated else None,
        chamado_por_nome=nome_usuario(request),
    )


def registrar_chamada_limitada(
    setor,
    acolhimento,
    request=None,
    local_destino="",
    observacao="",
    visivel_painel=True,
):
    total = total_chamadas_setor(setor, acolhimento)

    if total >= MAX_CHAMADAS_POR_SETOR:
        return None, total

    chamada = registrar_chamada(
        setor,
        acolhimento,
        request,
        local_destino=local_destino,
        observacao=observacao,
        visivel_painel=visivel_painel,
    )

    return chamada, total + 1


def registrar_ausencia(
    setor,
    acolhimento,
    request=None,
    local_destino="",
    observacao="",
):
    return registrar_chamada(
        setor,
        acolhimento,
        request,
        local_destino=local_destino,
        observacao=observacao or "Paciente ausente apos 4 chamadas.",
        tipo=ChamadaPainel.AUSENCIA,
    )


def registrar_retorno(
    setor,
    acolhimento,
    request=None,
    local_destino="",
    observacao="",
):
    return registrar_chamada(
        setor,
        acolhimento,
        request,
        local_destino=local_destino,
        observacao=observacao or "Paciente retornou para a fila.",
        tipo=ChamadaPainel.RETORNO,
    )


def marcar_acolhimento_ausente(acolhimento):
    acolhimento.status_antes_ausencia = acolhimento.status
    acolhimento.data_ausente = timezone.now()
    acolhimento.status = "AUSENTE"
    acolhimento.save(
        update_fields=[
            "status",
            "status_antes_ausencia",
            "data_ausente",
        ]
    )


def reativar_acolhimento_ausente(acolhimento, status_padrao):
    status_retorno = acolhimento.status_antes_ausencia or status_padrao
    acolhimento.status = status_retorno
    acolhimento.status_antes_ausencia = ""
    acolhimento.data_ausente = None
    acolhimento.save(
        update_fields=[
            "status",
            "status_antes_ausencia",
            "data_ausente",
        ]
    )

    return status_retorno
