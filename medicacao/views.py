from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from medico.models import ConsultaMedica

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
        .filter(
            solicita_medicacao=True,
            medicacao_realizada=False,
        )
        .exclude(acolhimento__status="FINALIZADO")
        .order_by("data_consulta")
    )

    medicacoes_realizadas = (
        ConsultaMedica.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .filter(
            solicita_medicacao=True,
            medicacao_realizada=True,
        )
        .order_by("-data_medicacao")
    )

    return render(
        request,
        "medicacao/dashboard.html",
        {
            "medicacoes_pendentes": medicacoes_pendentes,
            "medicacoes_realizadas": medicacoes_realizadas,
            "total_pendentes": medicacoes_pendentes.count(),
            "total_realizadas": medicacoes_realizadas.count(),
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
        form = MedicacaoForm(instance=consulta)

    return render(
        request,
        "medicacao/administrar.html",
        {
            "form": form,
            "consulta": consulta,
            "acolhimento": consulta.acolhimento,
        }
    )