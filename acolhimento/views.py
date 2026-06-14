from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Acolhimento


def tipo_atendimento(request):

    paciente = None
    erro = None

    cpf = request.GET.get('cpf')
    nome = request.GET.get('nome')

    if cpf or nome:
        paciente = Acolhimento.objects.filter(
            Q(cpf__icontains=cpf) |
            Q(nome_paciente__icontains=nome)
        ).first()

        if not paciente:
            erro = "Paciente não encontrado."

    if request.method == 'POST':

        sinais_obrigatorios = [
            'pressao_arterial',
            'temperatura',
            'frequencia_respiratoria',
            'pulso',
            'dor'
        ]

        for campo in sinais_obrigatorios:
            if not request.POST.get(campo):
                return render(request, 'acolhimento/tipo_atendimento.html', {
                    'erro': '⚠️ Todos os sinais vitais são obrigatórios.',
                    'paciente': paciente
                })

        temperatura = request.POST.get('temperatura')
        if temperatura:
            temperatura = float(temperatura.replace(',', '.'))

        idade = request.POST.get('idade')
        idade = int(idade) if idade and idade.isdigit() else None

        Acolhimento.objects.create(
            nome_paciente=request.POST.get('nome_paciente'),
            cpf=request.POST.get('cpf'),
            data_nascimento=request.POST.get('data_nascimento'),
            idade=idade,
            pressao_arterial=request.POST.get('pressao_arterial'),
            temperatura=temperatura,
            frequencia_respiratoria=request.POST.get('frequencia_respiratoria'),
            pulso=request.POST.get('pulso'),
            dor=request.POST.get('dor'),
            tipo_atendimento=request.POST.get('tipo_atendimento')
        )

        messages.success(request, "✔️ Atendimento registrado com sucesso!")

        return redirect('tipo_atendimento')

    return render(request, 'acolhimento/tipo_atendimento.html', {
        'paciente': paciente,
        'erro': erro
    })

def atendimento_normal(request):
    return render(request, 'acolhimento/normal.html')


def triagem_risco(request):
    return render(request, 'acolhimento/risco.html')


def atendimento_preferencial(request):
    return render(request, 'acolhimento/preferencial.html')