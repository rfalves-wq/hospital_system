from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Acolhimento


def tipo_atendimento(request):

    paciente = None
    erro = None

    # =========================
    # 🔍 BUSCA (GET)
    # =========================
    cpf = request.GET.get('cpf')
    nome = request.GET.get('nome')

    if cpf or nome:
        filtros = Q()

        if cpf:
            filtros |= Q(cpf__icontains=cpf)

        if nome:
            filtros |= Q(nome_paciente__icontains=nome)

        paciente = Acolhimento.objects.filter(filtros).first()

        if not paciente:
            erro = "Paciente não encontrado."

    # =========================
    # 💾 SALVAR (POST)
    # =========================
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

        # 🔥 tratamento de temperatura
        temperatura = request.POST.get('temperatura')
        try:
            temperatura = float(temperatura.replace(',', '.'))
        except (ValueError, AttributeError):
            return render(request, 'acolhimento/tipo_atendimento.html', {
                'erro': '⚠️ Temperatura inválida.',
                'paciente': paciente
            })

        # 🔢 idade segura
        idade = request.POST.get('idade')
        idade = int(idade) if idade and idade.isdigit() else None

        # 💾 salvar
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