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