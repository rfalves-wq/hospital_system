from django.shortcuts import render
from acolhimento.models import Acolhimento


def classificacao_dashboard(request):

    acolhimentos = (
        Acolhimento.objects
        .select_related("paciente")
        .filter(status="CLASSIFICACAO")
        .order_by("data_acolhimento")
    )

    return render(
        request,
        "classificacao/dashboard.html",
        {
            "acolhimentos": acolhimentos
        }
    )
    
from django.shortcuts import render, redirect, get_object_or_404
from acolhimento.models import Acolhimento
from .forms import ClassificacaoForm


def classificar_paciente(request, acolhimento_id):

    acolhimento = get_object_or_404(
        Acolhimento,
        id=acolhimento_id
    )

    if request.method == "POST":

        form = ClassificacaoForm(request.POST)

        if form.is_valid():

            classificacao = form.save(commit=False)

            classificacao.acolhimento = acolhimento

            classificacao.save()

            acolhimento.status = "CONSULTA"
            acolhimento.save()

            return redirect("classificacao_dashboard")

    else:

        form = ClassificacaoForm()

    return render(
        request,
        "classificacao/classificar.html",
        {
            "form": form,
            "acolhimento": acolhimento,
        }
    )