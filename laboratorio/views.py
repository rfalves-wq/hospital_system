from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

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
        .filter(
            solicita_exames_laboratoriais=True,
            exames_laboratoriais_realizados=False,
        )
        .exclude(acolhimento__status="FINALIZADO")
        .order_by("data_consulta")
    )

    exames_realizados = (
        ConsultaMedica.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .filter(
            solicita_exames_laboratoriais=True,
            exames_laboratoriais_realizados=True,
        )
        .order_by("-data_resultado_laboratorio")
    )

    return render(
        request,
        "laboratorio/dashboard.html",
        {
            "exames_pendentes": exames_pendentes,
            "exames_realizados": exames_realizados,
            "total_pendentes": exames_pendentes.count(),
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

        form = ResultadoLaboratorioForm(instance=consulta)

    return render(
        request,
        "laboratorio/lancar_resultado.html",
        {
            "form": form,
            "consulta": consulta,
            "acolhimento": consulta.acolhimento,
        }
    )