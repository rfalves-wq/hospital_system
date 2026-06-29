from datetime import date

from django.shortcuts import render, redirect, get_object_or_404

from acolhimento.models import Acolhimento
from .forms import RecepcaoForm
from .models import Recepcao


def recepcao_dashboard(request):

    acolhimentos = (
        Acolhimento.objects
        .select_related("paciente")
        .filter(
            data_acolhimento__date=date.today(),
            status="RECEPCAO"
        )
        .order_by("-data_acolhimento")
    )

    return render(
        request,
        "recepcao/dashboard.html",
        {
            "acolhimentos": acolhimentos
        }
    )


def cadastrar_paciente(request, acolhimento_id):

    acolhimento = get_object_or_404(Acolhimento, id=acolhimento_id)

    paciente_existente = Recepcao.objects.filter(cpf=acolhimento.cpf).first()

    if request.method == "POST":

        if paciente_existente:
            form = RecepcaoForm(request.POST, instance=paciente_existente)
        else:
            form = RecepcaoForm(request.POST)

        print("===== DADOS RECEBIDOS =====")
        print(request.POST)

        if form.is_valid():

            print("FORMULÁRIO VÁLIDO")

            paciente = form.save()

            acolhimento.paciente = paciente
            acolhimento.status = "CLASSIFICACAO"
            acolhimento.save()

            print("SALVOU COM SUCESSO")

            return redirect("recepcao_dashboard")

        else:

            print("FORMULÁRIO INVÁLIDO")
            print(form.errors)

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
        }
    )

def enviar_classificacao(request, acolhimento_id):

    acolhimento = get_object_or_404(Acolhimento, id=acolhimento_id)

    if acolhimento.paciente:

        acolhimento.status = "CLASSIFICACAO"
        acolhimento.save()

    return redirect("recepcao_dashboard")