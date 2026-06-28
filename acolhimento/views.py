from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
from .models import Acolhimento


def tipo_atendimento(request):

    erro = None

    if request.method == "POST":

        sinais_obrigatorios = [
            "pressao_arterial",
            "temperatura",
            "frequencia_respiratoria",
            "pulso",
            "dor",
        ]

        for campo in sinais_obrigatorios:
            if not request.POST.get(campo):
                return render(request, "acolhimento/tipo_atendimento.html", {
                    "erro": "⚠️ Todos os sinais vitais são obrigatórios."
                })

        temperatura = request.POST.get("temperatura")
        if temperatura:
            temperatura = float(temperatura.replace(",", "."))

        idade = request.POST.get("idade")
        idade = int(idade) if idade and idade.isdigit() else None
        acolhimento = Acolhimento.objects.filter(
            cpf=request.POST.get("cpf")
        ).exclude(
            status="FINALIZADO"
        ).first()
        if acolhimento:

            acolhimento.pressao_arterial = request.POST.get("pressao_arterial")
            acolhimento.temperatura = temperatura
            acolhimento.frequencia_respiratoria = request.POST.get("frequencia_respiratoria")
            acolhimento.pulso = request.POST.get("pulso")
            acolhimento.dor = request.POST.get("dor")
            acolhimento.tipo_atendimento = request.POST.get("tipo_atendimento")

            # garante que ele volte para a fila da recepção
            acolhimento.status = "RECEPCAO"

            acolhimento.save()

            paciente = acolhimento

        else:

            paciente = Acolhimento.objects.create(
                nome_paciente=request.POST.get("nome_paciente"),
                cpf=request.POST.get("cpf"),
                data_nascimento=request.POST.get("data_nascimento"),
                idade=idade,
                pressao_arterial=request.POST.get("pressao_arterial"),
                temperatura=temperatura,
                frequencia_respiratoria=request.POST.get("frequencia_respiratoria"),
                pulso=request.POST.get("pulso"),
                dor=request.POST.get("dor"),
                tipo_atendimento=request.POST.get("tipo_atendimento"),
            )

        messages.success(request, f"✔️ Atendimento registrado! BAM: {paciente.numero_bam}")

        return redirect("tipo_atendimento")

    return render(request, "acolhimento/tipo_atendimento.html", {"erro": erro})

# ==================================
# BUSCA AUTOMÁTICA AJAX
# ==================================

def buscar_paciente(request):

    busca = request.GET.get("busca", "")

    pacientes = Acolhimento.objects.filter(
        Q(nome_paciente__icontains=busca)
        | Q(cpf__icontains=busca)
    )[:20]

    dados = []

    for paciente in pacientes:
        dados.append({
            "nome": paciente.nome_paciente,
            "cpf": paciente.cpf,
            "numero_bam": paciente.numero_bam,
            "data_nascimento": (
                paciente.data_nascimento.strftime("%Y-%m-%d")
                if paciente.data_nascimento
                else ""
            ),
            "idade": paciente.idade or "",
        })

    return JsonResponse(dados, safe=False)


# ==================================
# TELAS
# ==================================

def atendimento_normal(request):
    return render(
        request,
        "acolhimento/normal.html"
    )


def triagem_risco(request):
    return render(
        request,
        "acolhimento/risco.html"
    )


def atendimento_preferencial(request):
    return render(
        request,
        "acolhimento/preferencial.html"
    )