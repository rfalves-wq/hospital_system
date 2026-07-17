from datetime import datetime, time

from django.db.models import Q
from django.utils import timezone

from .models import Acolhimento


def periodo_do_dia(data_hora=None):
    referencia = data_hora or timezone.now()

    if timezone.is_aware(referencia):
        referencia = timezone.localtime(referencia)

    data_referencia = referencia.date()

    inicio = datetime.combine(data_referencia, time.min)
    fim = datetime.combine(data_referencia, time.max)

    if timezone.is_aware(referencia):
        fuso = timezone.get_current_timezone()
        inicio = timezone.make_aware(inicio, fuso)
        fim = timezone.make_aware(fim, fuso)

    return inicio, fim


def filtro_mesmo_paciente(acolhimento):
    cpf = (acolhimento.cpf or "").strip()

    if not cpf and acolhimento.paciente:
        cpf = (acolhimento.paciente.cpf or "").strip()

    if cpf:
        return Q(cpf=cpf) | Q(paciente__cpf=cpf)

    nome = (
        acolhimento.paciente.nome_completo
        if acolhimento.paciente
        else acolhimento.nome_paciente
    )

    filtro = Q(nome_paciente__iexact=nome)

    if acolhimento.data_nascimento:
        filtro &= Q(data_nascimento=acolhimento.data_nascimento)

    return filtro


def passagens_do_paciente_no_dia(acolhimento, data_hora=None):
    referencia = data_hora or acolhimento.data_acolhimento or timezone.now()
    inicio, fim = periodo_do_dia(referencia)

    passagens = (
        Acolhimento.objects
        .select_related("paciente")
        .filter(
            filtro_mesmo_paciente(acolhimento),
            data_acolhimento__gte=inicio,
            data_acolhimento__lte=fim,
        )
        .order_by("data_acolhimento")
    )

    return inicio, fim, passagens


def chave_cache_passagens(acolhimento, inicio):
    cpf = (acolhimento.cpf or "").strip()

    if not cpf and acolhimento.paciente:
        cpf = (acolhimento.paciente.cpf or "").strip()

    if cpf:
        return ("cpf", inicio.date().isoformat(), cpf)

    nome = (
        acolhimento.paciente.nome_completo
        if acolhimento.paciente
        else acolhimento.nome_paciente
    )

    return (
        "nome",
        inicio.date().isoformat(),
        (nome or "").strip().lower(),
        acolhimento.data_nascimento.isoformat() if acolhimento.data_nascimento else "",
    )


def anexar_passagens_do_dia(acolhimentos, cache_passagens=None):
    lista = list(acolhimentos)
    cache_passagens = cache_passagens if cache_passagens is not None else {}

    for acolhimento in lista:
        referencia = acolhimento.data_acolhimento or timezone.now()
        inicio, fim = periodo_do_dia(referencia)
        cache_key = chave_cache_passagens(acolhimento, inicio)

        if cache_key not in cache_passagens:
            _inicio, _fim, passagens = passagens_do_paciente_no_dia(
                acolhimento,
                referencia,
            )
            cache_passagens[cache_key] = (_inicio, _fim, list(passagens))

        inicio, fim, passagens = cache_passagens[cache_key]

        acolhimento.periodo_passagens_inicio = inicio
        acolhimento.periodo_passagens_fim = fim
        acolhimento.passagens_hospital_dia = passagens
        acolhimento.total_passagens_hospital_dia = len(passagens)
        acolhimento.tem_passagem_anterior_hoje = any(
            passagem.id != acolhimento.id
            for passagem in passagens
        )

    return lista


def _formatar_data_hora(data_hora):
    if not data_hora:
        return "-"

    if timezone.is_aware(data_hora):
        data_hora = timezone.localtime(data_hora)

    return data_hora.strftime("%d/%m/%Y %H:%M")


def _formatar_hora(acolhimento):
    if acolhimento.hora_chegada:
        return acolhimento.hora_chegada.strftime("%H:%M")

    if acolhimento.data_acolhimento:
        data_hora = acolhimento.data_acolhimento

        if timezone.is_aware(data_hora):
            data_hora = timezone.localtime(data_hora)

        return data_hora.strftime("%H:%M")

    return "-"


def resumo_passagens_json(acolhimento, data_hora=None):
    inicio, fim, passagens = passagens_do_paciente_no_dia(acolhimento, data_hora)
    passagens = list(passagens)

    return {
        "total": len(passagens),
        "tem_passagem_anterior": any(
            passagem.id != acolhimento.id
            for passagem in passagens
        ),
        "periodo_inicio": inicio.strftime("%d/%m/%Y 00:00:00"),
        "periodo_fim": fim.strftime("%d/%m/%Y 23:59:59"),
        "passagens": [
            {
                "bam": passagem.numero_bam or "-",
                "data": _formatar_data_hora(passagem.data_acolhimento),
                "hora": _formatar_hora(passagem),
                "tipo": passagem.get_tipo_atendimento_display(),
                "status": passagem.get_status_display(),
                "atual": passagem.id == acolhimento.id,
            }
            for passagem in passagens
        ],
    }
