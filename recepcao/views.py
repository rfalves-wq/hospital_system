from datetime import date

from django.shortcuts import render, redirect, get_object_or_404

import acolhimento
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

from django.shortcuts import get_object_or_404, redirect, render

def cadastrar_paciente(request, acolhimento_id):

    acolhimento = get_object_or_404(Acolhimento, id=acolhimento_id)

    if request.method == "POST":

        form = RecepcaoForm(request.POST)

        print("===== DADOS RECEBIDOS =====")
        print(request.POST)

        if form.is_valid():

            print("FORMULÁRIO VÁLIDO")

            cpf = form.cleaned_data["cpf"]

            paciente = Recepcao.objects.filter(cpf=cpf).first()

            if paciente is None:
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
        }
    )