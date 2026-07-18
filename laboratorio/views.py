from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from acolhimento.tempos import anexar_entrada_setor
from accounts.utils import nome_profissional_request
from medico.models import ConsultaMedica

from .forms import ResultadoLaboratorioForm


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
        and not consulta.exames_imagem_realizados
    )

    return not medicacao_pendente and not laboratorio_pendente and not imagem_pendente


def laboratorio_dashboard(request):

    exames_pendentes = (
        ConsultaMedica.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .prefetch_related("acolhimento__tempos_setores")
        .filter(
            solicita_exames_laboratoriais=True,
            exames_laboratoriais_realizados=False,
        )
        .exclude(acolhimento__status__in=["FINALIZADO", "AUSENTE"])
        .order_by("data_consulta")
    )

    exames_realizados = (
        ConsultaMedica.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .prefetch_related("acolhimento__tempos_setores")
        .filter(
            solicita_exames_laboratoriais=True,
            exames_laboratoriais_realizados=True,
        )
        .order_by("-data_resultado_laboratorio")
    )

    exames_pendentes = anexar_entrada_setor(
        exames_pendentes,
        "LABORATORIO",
        attr_acolhimento="acolhimento",
        fallback_attr="data_consulta",
    )

    return render(
        request,
        "laboratorio/dashboard.html",
        {
            "exames_pendentes": exames_pendentes,
            "exames_realizados": exames_realizados,
            "total_pendentes": len(exames_pendentes),
            "total_realizados": exames_realizados.count(),
        }
    )


def lancar_resultado_laboratorio(request, consulta_id):

    consulta = get_object_or_404(
        ConsultaMedica.objects.select_related(
            "acolhimento",
            "acolhimento__paciente"
        ),
        id=consulta_id,
        solicita_exames_laboratoriais=True,
    )

    if request.method == "POST":

        form = ResultadoLaboratorioForm(
            request.POST,
            instance=consulta
        )

        if form.is_valid():

            consulta = form.save(commit=False)

            consulta.exames_laboratoriais_realizados = True
            consulta.data_resultado_laboratorio = timezone.now()

            consulta.save()

            acolhimento = consulta.acolhimento

            if procedimentos_finalizados(consulta):
                acolhimento.status = "RETORNO_MEDICO"
            else:
                acolhimento.status = "PROCEDIMENTOS"

            acolhimento.save()

            messages.success(
                request,
                "Resultado laboratorial salvo com sucesso."
            )

            return redirect("laboratorio_dashboard")

    else:

        initial = {}

        if not consulta.tecnico_laboratorio_nome:
            initial["tecnico_laboratorio_nome"] = nome_profissional_request(request)

        form = ResultadoLaboratorioForm(instance=consulta, initial=initial)

    return render(
        request,
        "laboratorio/lancar_resultado.html",
        {
            "form": form,
            "consulta": consulta,
            "acolhimento": consulta.acolhimento,
        }
    )
