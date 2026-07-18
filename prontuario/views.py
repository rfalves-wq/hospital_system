import re

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render

from acolhimento.models import Acolhimento
from acolhimento.tempos import formatar_duracao, somar_tempo_hospital
from internacao.models import Internacao
from medico.models import ConsultaMedica
from recepcao.models import Recepcao


def objeto_relacionado(objeto, atributo):
    try:
        return getattr(objeto, atributo)
    except ObjectDoesNotExist:
        return None


def busca_acolhimento(termo):
    return (
        Q(numero_bam__icontains=termo)
        | Q(nome_paciente__icontains=termo)
        | Q(cpf__icontains=termo)
        | Q(paciente__nome_completo__icontains=termo)
        | Q(paciente__nome_social__icontains=termo)
        | Q(paciente__cpf__icontains=termo)
        | Q(paciente__cns__icontains=termo)
    )


def query_acolhimentos(filtro):
    return (
        Acolhimento.objects
        .select_related(
            "paciente",
            "classificacao",
            "consulta_medica",
            "internacao",
        )
        .prefetch_related(
            "tempos_setores",
            "consulta_medica__transferencias_medico",
            "consulta_medica__reavaliacoes",
            "internacao__evolucoes",
        )
        .filter(filtro)
        .distinct()
        .order_by("-data_acolhimento")
    )


def montar_registros(acolhimentos):
    registros = []

    for acolhimento in acolhimentos:
        classificacao = objeto_relacionado(acolhimento, "classificacao")
        consulta = objeto_relacionado(acolhimento, "consulta_medica")
        internacao = objeto_relacionado(acolhimento, "internacao")
        tempos_setores = list(acolhimento.tempos_setores.all())
        tempo_total_hospital = somar_tempo_hospital(tempos_setores)

        registros.append({
            "acolhimento": acolhimento,
            "classificacao": classificacao,
            "consulta": consulta,
            "internacao": internacao,
            "tempos_setores": tempos_setores,
            "tempo_total_hospital": formatar_duracao(tempo_total_hospital),
            "transferencias": (
                list(consulta.transferencias_medico.all())
                if consulta
                else []
            ),
            "reavaliacoes_medicas": (
                list(consulta.reavaliacoes.all())
                if consulta
                else []
            ),
            "evolucoes": (
                list(internacao.evolucoes.all())
                if internacao
                else []
            ),
        })

    return registros


def adicionar_alerta_unico(lista, vistos, texto):
    texto = " ".join((texto or "").split())

    if not texto:
        return

    chave = texto.casefold()

    if chave in vistos:
        return

    vistos.add(chave)
    lista.append(texto)


def dividir_texto_alerta(texto):
    texto = (texto or "").strip()

    if not texto:
        return []

    partes = re.split(r"[\r\n;,|]+", texto)

    return [
        " ".join(parte.split())
        for parte in partes
        if " ".join(parte.split())
    ]


def coletar_alertas(registros):
    alergias = []
    medicamentos_em_uso = []
    alergias_vistas = set()
    medicamentos_vistos = set()

    for registro in registros:
        classificacao = registro["classificacao"]

        if not classificacao:
            continue

        for alergia in dividir_texto_alerta(classificacao.alergia):
            adicionar_alerta_unico(alergias, alergias_vistas, alergia)

        for medicamento in dividir_texto_alerta(classificacao.uso_medicamento):
            adicionar_alerta_unico(
                medicamentos_em_uso,
                medicamentos_vistos,
                medicamento
            )

    return alergias, medicamentos_em_uso


def contexto_prontuario(paciente, registros, termo="", atendimento_base=None):
    alergias, medicamentos_em_uso = coletar_alertas(registros)
    consultas = [registro["consulta"] for registro in registros if registro["consulta"]]
    internacoes = [registro["internacao"] for registro in registros if registro["internacao"]]

    return {
        "paciente": paciente,
        "registros": registros,
        "termo": termo,
        "atendimento_base": atendimento_base,
        "total_atendimentos": len(registros),
        "total_consultas": len(consultas),
        "total_internacoes": len(internacoes),
        "ultima_passagem": (
            registros[0]["acolhimento"].data_acolhimento
            if registros
            else None
        ),
        "alergias": alergias,
        "medicamentos_em_uso": medicamentos_em_uso,
    }


@login_required
def prontuario_dashboard(request):
    termo = request.GET.get("q", "").strip()

    pacientes = Recepcao.objects.annotate(
        total_atendimentos=Count("acolhimentos", distinct=True),
        ultima_passagem=Max("acolhimentos__data_acolhimento"),
    )

    atendimentos_avulsos = Acolhimento.objects.none()

    if termo:
        pacientes = pacientes.filter(
            Q(nome_completo__icontains=termo)
            | Q(nome_social__icontains=termo)
            | Q(cpf__icontains=termo)
            | Q(cns__icontains=termo)
            | Q(telefone__icontains=termo)
            | Q(acolhimentos__numero_bam__icontains=termo)
            | Q(acolhimentos__nome_paciente__icontains=termo)
            | Q(acolhimentos__cpf__icontains=termo)
        ).distinct()

        atendimentos_avulsos = (
            Acolhimento.objects
            .select_related("paciente")
            .filter(paciente__isnull=True)
            .filter(busca_acolhimento(termo))
            .order_by("-data_acolhimento")[:20]
        )
    else:
        pacientes = pacientes.filter(acolhimentos__isnull=False).distinct()

    pacientes = pacientes.order_by("-ultima_passagem", "nome_completo")[:40]

    return render(
        request,
        "prontuario/dashboard.html",
        {
            "termo": termo,
            "pacientes": pacientes,
            "atendimentos_avulsos": atendimentos_avulsos,
            "total_pacientes": Recepcao.objects.count(),
            "total_atendimentos": Acolhimento.objects.count(),
            "total_consultas": ConsultaMedica.objects.count(),
            "total_internacoes": Internacao.objects.count(),
        },
    )


@login_required
def prontuario_paciente(request, paciente_id):
    paciente = get_object_or_404(Recepcao, id=paciente_id)
    filtro = Q(paciente=paciente)

    if paciente.cpf:
        filtro |= Q(cpf=paciente.cpf) | Q(paciente__cpf=paciente.cpf)

    acolhimentos = query_acolhimentos(filtro)
    registros = montar_registros(acolhimentos)

    return render(
        request,
        "prontuario/detalhe.html",
        contexto_prontuario(
            paciente=paciente,
            registros=registros,
            termo=request.GET.get("q", "").strip(),
        ),
    )


@login_required
def prontuario_atendimento(request, acolhimento_id):
    acolhimento = get_object_or_404(
        Acolhimento.objects.select_related("paciente"),
        id=acolhimento_id,
    )

    if acolhimento.paciente_id:
        return redirect("prontuario_paciente", paciente_id=acolhimento.paciente_id)

    if acolhimento.cpf:
        filtro = Q(cpf=acolhimento.cpf) | Q(paciente__cpf=acolhimento.cpf)
    else:
        filtro = Q(nome_paciente__iexact=acolhimento.nome_paciente)

        if acolhimento.data_nascimento:
            filtro &= Q(data_nascimento=acolhimento.data_nascimento)

    acolhimentos = query_acolhimentos(filtro)
    registros = montar_registros(acolhimentos)

    return render(
        request,
        "prontuario/detalhe.html",
        contexto_prontuario(
            paciente=None,
            registros=registros,
            termo=request.GET.get("q", "").strip(),
            atendimento_base=acolhimento,
        ),
    )
