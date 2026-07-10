from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from acolhimento.models import Acolhimento
from acolhimento.utils import (
    anexar_passagens_do_dia,
    passagens_do_paciente_no_dia,
    periodo_do_dia,
)

from .forms import ClassificacaoForm
from .models import ClassificacaoRisco


def classificacao_dashboard(request):
    periodo_inicio, periodo_fim = periodo_do_dia(timezone.now())

    acolhimentos = (
        Acolhimento.objects
        .select_related("paciente")
        .filter(
            status="CLASSIFICACAO",
            ausente_classificacao=False,
        )
        .order_by("data_acolhimento")
    )

    ausentes_classificacao = (
        Acolhimento.objects
        .select_related("paciente")
        .filter(
            status="CLASSIFICACAO",
            ausente_classificacao=True,
        )
        .order_by("-data_ausente_classificacao", "data_acolhimento")
    )

    classificados_hoje = (
        ClassificacaoRisco.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .filter(
            data_classificacao__gte=periodo_inicio,
            data_classificacao__lte=periodo_fim,
        )
        .order_by("-data_classificacao")
    )

    return render(
        request,
        "classificacao/dashboard.html",
        {
            "acolhimentos": anexar_passagens_do_dia(acolhimentos),
            "ausentes_classificacao": anexar_passagens_do_dia(ausentes_classificacao),
            "total_ausentes_classificacao": ausentes_classificacao.count(),
            "classificados_hoje": classificados_hoje,
            "total_classificados_hoje": classificados_hoje.count(),
            "periodo_classificacao_inicio": periodo_inicio,
            "periodo_classificacao_fim": periodo_fim,
        }
    )


def classificar_paciente(request, acolhimento_id):
    acolhimento = get_object_or_404(
        Acolhimento.objects.select_related("paciente"),
        id=acolhimento_id
    )

    periodo_inicio, periodo_fim, passagens_hospital_dia = passagens_do_paciente_no_dia(acolhimento)

    if request.method == "POST":
        form = ClassificacaoForm(request.POST)

        if form.is_valid():
            classificacao = form.save(commit=False)
            classificacao.acolhimento = acolhimento
            classificacao.save()

            acolhimento.status = "CONSULTA"
            acolhimento.ausente_classificacao = False
            acolhimento.data_ausente_classificacao = None
            acolhimento.save(
                update_fields=[
                    "status",
                    "ausente_classificacao",
                    "data_ausente_classificacao",
                ]
            )

            return redirect("classificacao_dashboard")

    else:
        form = ClassificacaoForm()

    return render(
        request,
        "classificacao/classificar.html",
        {
            "form": form,
            "acolhimento": acolhimento,
            "periodo_passagens_inicio": periodo_inicio,
            "periodo_passagens_fim": periodo_fim,
            "passagens_hospital_dia": passagens_hospital_dia,
            "total_passagens_hospital_dia": passagens_hospital_dia.count(),
            "tem_passagem_anterior_hoje": (
                passagens_hospital_dia
                .exclude(id=acolhimento.id)
                .exists()
            ),
        }
    )


def chamar_paciente_classificacao(request, acolhimento_id):
    if request.method != "POST":
        return redirect("classificacao_dashboard")

    acolhimento = get_object_or_404(
        Acolhimento,
        id=acolhimento_id,
        status="CLASSIFICACAO"
    )

    acolhimento.chamadas_classificacao += 1
    acolhimento.data_ultima_chamada_classificacao = timezone.now()
    acolhimento.ausente_classificacao = False
    acolhimento.data_ausente_classificacao = None
    acolhimento.save(
        update_fields=[
            "chamadas_classificacao",
            "data_ultima_chamada_classificacao",
            "ausente_classificacao",
            "data_ausente_classificacao",
        ]
    )

    messages.success(
        request,
        f"Chamada {acolhimento.chamadas_classificacao} registrada para o BAM {acolhimento.numero_bam}."
    )

    return redirect("classificacao_dashboard")


def ausentar_paciente_classificacao(request, acolhimento_id):
    if request.method != "POST":
        return redirect("classificacao_dashboard")

    acolhimento = get_object_or_404(
        Acolhimento,
        id=acolhimento_id,
        status="CLASSIFICACAO"
    )

    if acolhimento.chamadas_classificacao < 4:
        faltam = 4 - acolhimento.chamadas_classificacao
        messages.warning(
            request,
            f"Para ausentar o BAM {acolhimento.numero_bam}, registre mais {faltam} chamada(s)."
        )
        return redirect("classificacao_dashboard")

    acolhimento.ausente_classificacao = True
    acolhimento.data_ausente_classificacao = timezone.now()
    acolhimento.save(
        update_fields=[
            "ausente_classificacao",
            "data_ausente_classificacao",
        ]
    )

    messages.warning(
        request,
        f"BAM {acolhimento.numero_bam} marcado como ausente na classificação."
    )

    return redirect("classificacao_dashboard")
