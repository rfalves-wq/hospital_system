from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from medico.models import ConsultaMedica

from .forms import ResultadoImagemForm


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


def imagem_dashboard(request):

    exames_pendentes = (
        ConsultaMedica.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .filter(
            solicita_exames_imagem=True,
            exames_imagem_realizados=False,
        )
        .exclude(acolhimento__status="FINALIZADO")
        .order_by("data_consulta")
    )

    exames_realizados = (
        ConsultaMedica.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .filter(
            solicita_exames_imagem=True,
            exames_imagem_realizados=True,
        )
        .order_by("-data_resultado_imagem")
    )

    return render(
        request,
        "imagem/dashboard.html",
        {
            "exames_pendentes": exames_pendentes,
            "exames_realizados": exames_realizados,
            "total_pendentes": exames_pendentes.count(),
            "total_realizados": exames_realizados.count(),
        }
    )


def lancar_resultado_imagem(request, consulta_id):

    consulta = get_object_or_404(
        ConsultaMedica.objects.select_related(
            "acolhimento",
            "acolhimento__paciente"
        ),
        id=consulta_id,
        solicita_exames_imagem=True,
    )

    if request.method == "POST":

        form = ResultadoImagemForm(
            request.POST,
            instance=consulta
        )

        if form.is_valid():

            consulta = form.save(commit=False)

            consulta.exames_imagem_realizados = True
            consulta.data_resultado_imagem = timezone.now()

            consulta.save()

            acolhimento = consulta.acolhimento

            if procedimentos_finalizados(consulta):
                acolhimento.status = "RETORNO_MEDICO"
            else:
                acolhimento.status = "PROCEDIMENTOS"

            acolhimento.save()

            messages.success(
                request,
                "Resultado de imagem salvo com sucesso."
            )

            return redirect("imagem_dashboard")

    else:

        form = ResultadoImagemForm(instance=consulta)

    return render(
        request,
        "imagem/lancar_resultado.html",
        {
            "form": form,
            "consulta": consulta,
            "acolhimento": consulta.acolhimento,
        }
    )