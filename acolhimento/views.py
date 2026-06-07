from django.shortcuts import render

def tipo_atendimento(request):
    return render(request, 'acolhimento/tipo_atendimento.html')

def atendimento_normal(request):
    return render(request, 'acolhimento/normal.html')

def triagem_risco(request):
    return render(request, 'acolhimento/risco.html')

def atendimento_preferencial(request):
    return render(request, 'acolhimento/preferencial.html')