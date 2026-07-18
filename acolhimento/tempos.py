from datetime import datetime, timedelta

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

STATUS_SEM_SETOR_ABERTO = {"FINALIZADO"}
SETORES_FORA_TEMPO_HOSPITAL = {"AUSENTE"}


def setor_por_status(status):
    if status in STATUS_SEM_SETOR_ABERTO:
        return None

    return STATUS_PARA_SETOR.get(status)


def formatar_duracao(duracao):
    if not duracao:
        return "0min"

    total_segundos = max(0, int(duracao.total_seconds()))
    minutos_total = total_segundos // 60
    dias, resto_minutos = divmod(minutos_total, 24 * 60)
    horas, minutos = divmod(resto_minutos, 60)

    partes = []

    if dias:
        partes.append(f"{dias}d")

    if horas:
        partes.append(f"{horas}h")

    if minutos or not partes:
        partes.append(f"{minutos}min")

    return " ".join(partes)


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


def abrir_setor(
    acolhimento,
    setor,
    entrada=None,
    status_origem="",
    origem="STATUS",
    observacao="",
):
    from .models import PermanenciaSetorAtendimento

    if not acolhimento or not acolhimento.pk or not setor:
        return None

    aberto = (
        PermanenciaSetorAtendimento.objects
        .filter(
            acolhimento=acolhimento,
            setor=setor,
            origem=origem,
            saida__isnull=True,
        )
        .first()
    )

    if aberto:
        return aberto

    return PermanenciaSetorAtendimento.objects.create(
        acolhimento=acolhimento,
        setor=setor,
        entrada=entrada or timezone.now(),
        status_origem=status_origem or "",
        origem=origem,
        observacao=observacao or "",
    )


def fechar_setores_status(acolhimento, saida=None):
    from .models import PermanenciaSetorAtendimento

    if not acolhimento or not acolhimento.pk:
        return 0

    return (
        PermanenciaSetorAtendimento.objects
        .filter(
            acolhimento=acolhimento,
            origem="STATUS",
            saida__isnull=True,
        )
        .update(saida=saida or timezone.now())
    )


def fechar_setor(acolhimento, setor, saida=None, origem="PROCEDIMENTO"):
    from .models import PermanenciaSetorAtendimento

    if not acolhimento or not acolhimento.pk or not setor:
        return 0

    return (
        PermanenciaSetorAtendimento.objects
        .filter(
            acolhimento=acolhimento,
            setor=setor,
            origem=origem,
            saida__isnull=True,
        )
        .update(saida=saida or timezone.now())
    )


def criar_setor_fechado(
    acolhimento,
    setor,
    entrada,
    saida,
    status_origem="",
    origem="STATUS",
    observacao="",
):
    from .models import PermanenciaSetorAtendimento

    if not acolhimento or not acolhimento.pk or not setor:
        return None

    if saida < entrada:
        entrada = saida

    existente = PermanenciaSetorAtendimento.objects.filter(
        acolhimento=acolhimento,
        setor=setor,
        origem=origem,
        entrada=entrada,
        saida=saida,
    ).first()

    if existente:
        return existente

    return PermanenciaSetorAtendimento.objects.create(
        acolhimento=acolhimento,
        setor=setor,
        entrada=entrada,
        saida=saida,
        status_origem=status_origem or "",
        origem=origem,
        observacao=observacao or "",
    )


def garantir_acolhimento_inicial(acolhimento):
    from .models import PermanenciaSetorAtendimento

    if not acolhimento or not acolhimento.pk:
        return

    if PermanenciaSetorAtendimento.objects.filter(
        acolhimento=acolhimento,
        setor="ACOLHIMENTO",
        origem="STATUS",
    ).exists():
        return

    saida = acolhimento.data_acolhimento or timezone.now()
    entrada = data_hora_chegada(acolhimento)

    criar_setor_fechado(
        acolhimento,
        "ACOLHIMENTO",
        entrada,
        saida,
        status_origem="ACOLHIMENTO",
        origem="STATUS",
        observacao="Chegada ate registro do acolhimento.",
    )


def sincronizar_permanencia_status(acolhimento, status_anterior=None):
    from .models import PermanenciaSetorAtendimento

    if not acolhimento or not acolhimento.pk:
        return

    agora = timezone.now()
    status_atual = acolhimento.status or ""
    setor_atual = setor_por_status(status_atual)

    garantir_acolhimento_inicial(acolhimento)

    if status_anterior is None:
        if setor_atual:
            abrir_setor(
                acolhimento,
                setor_atual,
                entrada=acolhimento.data_acolhimento or agora,
                status_origem=status_atual,
                origem="STATUS",
            )
        return

    if status_anterior == status_atual:
        if setor_atual:
            abrir_setor(
                acolhimento,
                setor_atual,
                entrada=acolhimento.data_acolhimento or agora,
                status_origem=status_atual,
                origem="STATUS",
            )
        return

    setor_anterior = setor_por_status(status_anterior)
    fechados = fechar_setores_status(acolhimento, agora)

    if setor_anterior and not fechados:
        criar_setor_fechado(
            acolhimento,
            setor_anterior,
            acolhimento.data_acolhimento or agora,
            agora,
            status_origem=status_anterior,
            origem="STATUS",
            observacao="Periodo aproximado criado na primeira mudanca apos ativar o controle de tempo.",
        )

    if setor_atual:
        abrir_setor(
            acolhimento,
            setor_atual,
            entrada=agora,
            status_origem=status_atual,
            origem="STATUS",
        )


def sincronizar_procedimentos_consulta(consulta):
    if not consulta or not getattr(consulta, "acolhimento_id", None):
        return

    acolhimento = consulta.acolhimento
    entrada_base = consulta.data_consulta or timezone.now()

    if consulta.solicita_medicacao:
        abrir_setor(
            acolhimento,
            "MEDICACAO",
            entrada=entrada_base,
            origem="PROCEDIMENTO",
            observacao="Medicacao aguardando administracao.",
        )

        if consulta.farmacia_liberada:
            saida_farmacia = consulta.data_liberacao_farmacia or timezone.now()
            abrir_setor(
                acolhimento,
                "FARMACIA",
                entrada=entrada_base,
                origem="PROCEDIMENTO",
                observacao="Medicacao liberada pela farmacia.",
            )
            fechar_setor(
                acolhimento,
                "FARMACIA",
                saida=saida_farmacia,
                origem="PROCEDIMENTO",
            )

        else:
            fechar_setor(
                acolhimento,
                "FARMACIA",
                saida=consulta.data_medicacao or entrada_base,
                origem="PROCEDIMENTO",
            )

        if consulta.medicacao_realizada:
            fechar_setor(
                acolhimento,
                "MEDICACAO",
                saida=consulta.data_medicacao or timezone.now(),
                origem="PROCEDIMENTO",
            )

    if consulta.solicita_exames_laboratoriais:
        abrir_setor(
            acolhimento,
            "LABORATORIO",
            entrada=entrada_base,
            origem="PROCEDIMENTO",
            observacao="Exames laboratoriais aguardando resultado.",
        )

        if consulta.exames_laboratoriais_realizados:
            fechar_setor(
                acolhimento,
                "LABORATORIO",
                saida=consulta.data_resultado_laboratorio or timezone.now(),
                origem="PROCEDIMENTO",
            )

    if consulta.solicita_exames_imagem:
        abrir_setor(
            acolhimento,
            "IMAGEM",
            entrada=entrada_base,
            origem="PROCEDIMENTO",
            observacao="Exames de imagem aguardando resultado.",
        )

        if consulta.todos_exames_imagem_finalizados():
            fechar_setor(
                acolhimento,
                "IMAGEM",
                saida=consulta.data_resultado_imagem or timezone.now(),
                origem="PROCEDIMENTO",
            )


def somar_tempo_hospital(tempos):
    total = timedelta()
    agora = timezone.now()

    for tempo in tempos:
        if tempo.origem != "STATUS":
            continue

        if tempo.setor in SETORES_FORA_TEMPO_HOSPITAL:
            continue

        entrada = tempo.entrada
        saida = tempo.saida or agora

        if entrada and saida and saida >= entrada:
            total += saida - entrada

    return total


def tempos_do_acolhimento(acolhimento):
    if not acolhimento or not acolhimento.pk:
        return []

    cache = getattr(acolhimento, "_prefetched_objects_cache", {})

    if "tempos_setores" in cache:
        return list(cache["tempos_setores"])

    return list(acolhimento.tempos_setores.all())


def ultima_permanencia_setor(acolhimento, setor, origem=None):
    candidatos = [
        tempo
        for tempo in tempos_do_acolhimento(acolhimento)
        if tempo.setor == setor and (origem is None or tempo.origem == origem)
    ]

    if not candidatos:
        return None

    abertos = [tempo for tempo in candidatos if tempo.saida is None]

    if abertos:
        return max(abertos, key=lambda tempo: (tempo.entrada, tempo.id or 0))

    return max(candidatos, key=lambda tempo: (tempo.entrada, tempo.id or 0))


def entrada_setor(acolhimento, setor, origem=None, fallback=None):
    permanencia = ultima_permanencia_setor(acolhimento, setor, origem)

    if permanencia:
        return permanencia.entrada

    if fallback is not None:
        return fallback

    if setor == "ACOLHIMENTO":
        return data_hora_chegada(acolhimento)

    return getattr(acolhimento, "data_acolhimento", None)


def anexar_entrada_setor(
    objetos,
    setor,
    attr="entrada_setor_atual",
    attr_acolhimento=None,
    origem=None,
    fallback_attr=None,
    fallback_attrs=None,
):
    lista = list(objetos)
    nomes_fallback = []

    if fallback_attr:
        nomes_fallback.append(fallback_attr)

    if fallback_attrs:
        nomes_fallback.extend(fallback_attrs)

    for objeto in lista:
        acolhimento = (
            getattr(objeto, attr_acolhimento)
            if attr_acolhimento
            else objeto
        )
        fallback = None

        for nome_attr in nomes_fallback:
            fallback = getattr(objeto, nome_attr, None)

            if fallback is not None:
                break

        valor = entrada_setor(acolhimento, setor, origem=origem, fallback=fallback)
        setattr(objeto, attr, valor)

    return lista


def anexar_entrada_status_atual(objetos, attr="entrada_setor_atual", attr_acolhimento=None):
    lista = list(objetos)

    for objeto in lista:
        acolhimento = (
            getattr(objeto, attr_acolhimento)
            if attr_acolhimento
            else objeto
        )
        setor = setor_por_status(getattr(acolhimento, "status", ""))
        if setor:
            valor = entrada_setor(acolhimento, setor)
        else:
            tempos_status = [
                tempo
                for tempo in tempos_do_acolhimento(acolhimento)
                if tempo.origem == "STATUS" and tempo.setor not in SETORES_FORA_TEMPO_HOSPITAL
            ]
            ultimo_status = (
                max(tempos_status, key=lambda tempo: (tempo.entrada, tempo.id or 0))
                if tempos_status
                else None
            )
            valor = (
                ultimo_status.entrada
                if ultimo_status
                else getattr(acolhimento, "data_acolhimento", None)
            )
        setattr(objeto, attr, valor)

    return lista
