from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from acolhimento.tempos import anexar_entrada_setor
from accounts.utils import nome_profissional_request
from medico.models import ConsultaMedica
from painel.models import ChamadaPainel
from painel.services import (
    anexar_status_chamadas,
    marcar_acolhimento_ausente,
    registrar_ausencia,
    registrar_chamada_limitada,
    registrar_retorno,
    reativar_acolhimento_ausente,
    total_chamadas_setor,
)

from .forms import MedicacaoForm


def procedimentos_finalizados(consulta):
    medicacao_pendente = (
        consulta.solicita_medicacao
        and not consulta.medicacao_realizada
    )

    laboratorio_pendente = (
        consulta.solicita_exames_laboratoriais
        and not consulta.exames_laboratoriais_realizados
    )

    imagem_pendente = (
        consulta.solicita_exames_imagem
        and not consulta.todos_exames_imagem_finalizados()
    )

    return not medicacao_pendente and not laboratorio_pendente and not imagem_pendente


def medicacao_dashboard(request):
    medicacoes_pendentes = (
        ConsultaMedica.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .prefetch_related("acolhimento__tempos_setores")
        .filter(
            solicita_medicacao=True,
            medicacao_realizada=False,
        )
        .exclude(acolhimento__status__in=["FINALIZADO", "AUSENTE"])
        .order_by("data_consulta")
    )

    medicacoes_realizadas = (
        ConsultaMedica.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .prefetch_related("acolhimento__tempos_setores")
        .filter(
            solicita_medicacao=True,
            medicacao_realizada=True,
        )
        .order_by("-data_medicacao")
    )
    ausentes_medicacao = (
        ConsultaMedica.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .prefetch_related("acolhimento__tempos_setores")
        .filter(
            solicita_medicacao=True,
            medicacao_realizada=False,
            acolhimento__status="AUSENTE",
        )
        .filter(
            Q(acolhimento__status_antes_ausencia="PROCEDIMENTOS")
            | Q(
                acolhimento__status_antes_ausencia="",
                acolhimento__chamadas_painel__setor=ChamadaPainel.MEDICACAO,
                acolhimento__chamadas_painel__tipo=ChamadaPainel.AUSENCIA,
            )
        )
        .distinct()
        .order_by("-acolhimento__data_ausente", "data_consulta")
    )

    medicacoes_pendentes = anexar_entrada_setor(
        medicacoes_pendentes,
        "MEDICACAO",
        attr_acolhimento="acolhimento",
        fallback_attrs=["data_liberacao_farmacia", "data_consulta"],
    )
    anexar_status_chamadas(
        medicacoes_pendentes,
        ChamadaPainel.MEDICACAO,
        attr_acolhimento="acolhimento",
    )

    return render(
        request,
        "medicacao/dashboard.html",
        {
            "medicacoes_pendentes": medicacoes_pendentes,
            "medicacoes_realizadas": medicacoes_realizadas,
            "total_pendentes": len(medicacoes_pendentes),
            "total_realizadas": medicacoes_realizadas.count(),
            "ausentes_medicacao": ausentes_medicacao,
            "total_ausentes_medicacao": ausentes_medicacao.count(),
        }
    )


def administrar_medicacao(request, consulta_id):
    consulta = get_object_or_404(
        ConsultaMedica.objects.select_related(
            "acolhimento",
            "acolhimento__paciente"
        ),
        id=consulta_id,
        solicita_medicacao=True,
    )

    if request.method == "POST":
        form = MedicacaoForm(
            request.POST,
            instance=consulta
        )

        if form.is_valid():
            consulta = form.save(commit=False)

            consulta.medicacao_realizada = True
            consulta.data_medicacao = timezone.now()
            consulta.save()

            acolhimento = consulta.acolhimento

            if procedimentos_finalizados(consulta):
                acolhimento.status = "RETORNO_MEDICO"
            else:
                acolhimento.status = "PROCEDIMENTOS"

            acolhimento.save()

            messages.success(
                request,
                "Medicação registrada com sucesso."
            )

            return redirect("medicacao_dashboard")

    else:
        initial = {}

        if not consulta.profissional_medicacao_nome:
            initial["profissional_medicacao_nome"] = nome_profissional_request(request)

        form = MedicacaoForm(instance=consulta, initial=initial)

    return render(
        request,
        "medicacao/administrar.html",
        {
            "form": form,
            "consulta": consulta,
            "acolhimento": consulta.acolhimento,
        }
    )


def chamar_paciente_medicacao(request, consulta_id):
    if request.method != "POST":
        return redirect("medicacao_dashboard")

    consulta = get_object_or_404(
        ConsultaMedica.objects.select_related("acolhimento", "acolhimento__paciente"),
        id=consulta_id,
        solicita_medicacao=True,
        medicacao_realizada=False,
    )
    chamada, total = registrar_chamada_limitada(
        ChamadaPainel.MEDICACAO,
        consulta.acolhimento,
        request,
        local_destino="Sala de medicacao",
    )

    if not chamada:
        messages.warning(
            request,
            f"BAM {consulta.acolhimento.numero_bam} ja foi chamado 4 vezes. Use Ausentar."
        )
        return redirect("medicacao_dashboard")

    messages.success(
        request,
        f"Chamada {total}/4 registrada para o BAM {consulta.acolhimento.numero_bam} na medicacao."
    )

    return redirect("medicacao_dashboard")


def ausentar_paciente_medicacao(request, consulta_id):
    if request.method != "POST":
        return redirect("medicacao_dashboard")

    consulta = get_object_or_404(
        ConsultaMedica.objects.select_related("acolhimento", "acolhimento__paciente"),
        id=consulta_id,
        solicita_medicacao=True,
        medicacao_realizada=False,
    )
    acolhimento = consulta.acolhimento
    total = total_chamadas_setor(ChamadaPainel.MEDICACAO, acolhimento)

    if total < 4:
        faltam = 4 - total
        messages.warning(
            request,
            f"Para ausentar o BAM {acolhimento.numero_bam}, registre mais {faltam} chamada(s)."
        )
        return redirect("medicacao_dashboard")

    registrar_ausencia(
        ChamadaPainel.MEDICACAO,
        acolhimento,
        request,
        local_destino="Sala de medicacao",
    )
    marcar_acolhimento_ausente(acolhimento)

    messages.warning(
        request,
        f"BAM {acolhimento.numero_bam} marcado como ausente na medicacao."
    )

    return redirect("medicacao_dashboard")


def retornar_ausente_medicacao(request, consulta_id):
    if request.method != "POST":
        return redirect("medicacao_dashboard")

    consulta = get_object_or_404(
        ConsultaMedica.objects.select_related("acolhimento", "acolhimento__paciente"),
        id=consulta_id,
        solicita_medicacao=True,
        medicacao_realizada=False,
        acolhimento__status="AUSENTE",
    )
    acolhimento = consulta.acolhimento
    status_retorno = acolhimento.status_antes_ausencia or "PROCEDIMENTOS"

    if status_retorno != "PROCEDIMENTOS":
        messages.warning(
            request,
            f"BAM {acolhimento.numero_bam} esta ausente em outro setor."
        )
        return redirect("medicacao_dashboard")

    registrar_retorno(
        ChamadaPainel.MEDICACAO,
        acolhimento,
        request,
        local_destino="Sala de medicacao",
    )
    reativar_acolhimento_ausente(acolhimento, "PROCEDIMENTOS")

    messages.success(
        request,
        f"BAM {acolhimento.numero_bam} retornou para a fila de medicacao."
    )

    return redirect("medicacao_dashboard")
