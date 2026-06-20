from datetime import date
from django.shortcuts import render
from acolhimento.models import Acolhimento

def recepcao_dashboard(request):

    acolhimentos = Acolhimento.objects.filter(
        data_acolhimento__date=date.today()
    ).order_by('-data_acolhimento')

    return render(
        request,
        'recepcao/dashboard.html',
        {
            'acolhimentos': acolhimentos
        }
    )