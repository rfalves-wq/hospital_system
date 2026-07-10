from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from acolhimento.models import Acolhimento
from acolhimento.utils import anexar_passagens_do_dia, passagens_do_paciente_no_dia

from .forms import RecepcaoForm
from .models import Recepcao


def recepcao_dashboard(request):
    hoje = date.today()

    acolhimentos = (
        Acolhimento.objects
        .select_related("paciente")
        .filter(
            data_acolhimento__date=hoje,
            status="RECEPCAO"
        )
        .order_by("-data_acolhimento")
    )

    historico = (
        Acolhimento.objects
        .select_related("paciente")
        .filter(data_acolhimento__date=hoje)
        .exclude(status="RECEPCAO")
        .order_by("-data_acolhimento")
    )

    return render(
        request,
        "recepcao/dashboard.html",
        {
            "acolhimentos": anexar_passagens_do_dia(acolhimentos),
            "historico": anexar_passagens_do_dia(historico),
        }
    )


def cadastrar_paciente(request, acolhimento_id):
    acolhimento = get_object_or_404(
        Acolhimento.objects.select_related("paciente"),
        id=acolhimento_id
    )

    paciente_existente = Recepcao.objects.filter(cpf=acolhimento.cpf).first()
    periodo_inicio, periodo_fim, passagens_hospital_dia = passagens_do_paciente_no_dia(acolhimento)

    if request.method == "POST":

        if paciente_existente:
            form = RecepcaoForm(request.POST, instance=paciente_existente)
        else:
            form = RecepcaoForm(request.POST)

        if form.is_valid():
            paciente = form.save()

            acolhimento.paciente = paciente
            acolhimento.status = "CLASSIFICACAO"
            acolhimento.save()

            messages.success(
                request,
                f"Paciente {paciente.nome_completo} salvo e encaminhado para a Classificação de Risco."
            )

            return redirect("recepcao_dashboard")

    else:

        if paciente_existente:
            form = RecepcaoForm(instance=paciente_existente)
        else:
            form = RecepcaoForm(
                initial={
                    "nome_completo": acolhimento.nome_paciente,
                    "cpf": acolhimento.cpf,
                    "nascimento": acolhimento.data_nascimento,
                    "idade": acolhimento.idade,
                }
            )

    return render(
        request,
        "recepcao/cadastro.html",
        {
            "form": form,
            "acolhimento": acolhimento,
            "paciente_existente": paciente_existente,
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


def enviar_classificacao(request, acolhimento_id):
    acolhimento = get_object_or_404(Acolhimento, id=acolhimento_id)

    if acolhimento.paciente:
        acolhimento.status = "CLASSIFICACAO"
        acolhimento.save()

    return redirect("recepcao_dashboard")
