from datetime import datetime

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

from .models import Acolhimento
from .utils import periodo_do_dia, resumo_passagens_json


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
                return render(
                    request,
                    "acolhimento/tipo_atendimento.html",
                    {
                        "erro": "⚠️ Todos os sinais vitais são obrigatórios.",
                        "historico_acolhimentos": buscar_historico_acolhimentos(),
                    }
                )

        temperatura = request.POST.get("temperatura")

        try:
            temperatura = float(temperatura.replace(",", "."))
        except (ValueError, AttributeError):
            return render(
                request,
                "acolhimento/tipo_atendimento.html",
                {
                    "erro": "⚠️ Temperatura inválida.",
                    "historico_acolhimentos": buscar_historico_acolhimentos(),
                }
            )

        data_nascimento_str = request.POST.get("data_nascimento")

        try:
            data_nascimento = datetime.strptime(
                data_nascimento_str,
                "%Y-%m-%d"
            ).date()
        except (ValueError, TypeError):
            return render(
                request,
                "acolhimento/tipo_atendimento.html",
                {
                    "erro": "⚠️ Data de nascimento inválida.",
                    "historico_acolhimentos": buscar_historico_acolhimentos(),
                }
            )

        cpf = request.POST.get("cpf", "").strip()
        hora_chegada_str = request.POST.get("hora_chegada", "").strip()

        try:
            hora_chegada = datetime.strptime(
                hora_chegada_str,
                "%H:%M"
            ).time()
        except (ValueError, TypeError):
            hora_chegada = None

        paciente = Acolhimento.objects.create(
            nome_paciente=request.POST.get("nome_paciente"),
            cpf=cpf,
            data_nascimento=data_nascimento,
            hora_chegada=hora_chegada,
            pressao_arterial=request.POST.get("pressao_arterial"),
            temperatura=temperatura,
            frequencia_respiratoria=request.POST.get("frequencia_respiratoria"),
            pulso=request.POST.get("pulso"),
            dor=request.POST.get("dor"),
            tipo_atendimento=request.POST.get("tipo_atendimento"),
            status="RECEPCAO",
        )

        request.session["acolhimento_impressao_id"] = paciente.id

        messages.success(
            request,
            f"✔️ Atendimento registrado! Encaminhado para recepção. BAM: {paciente.numero_bam}"
        )

        return redirect("tipo_atendimento")

    dados_impressao = buscar_dados_impressao(request)

    return render(
        request,
        "acolhimento/tipo_atendimento.html",
        {
            "erro": erro,
            "historico_acolhimentos": buscar_historico_acolhimentos(),
            "dados_impressao": dados_impressao,
        }
    )


def buscar_dados_impressao(request):
    acolhimento_id = request.session.pop("acolhimento_impressao_id", None)

    if not acolhimento_id:
        return None

    try:
        acolhimento = Acolhimento.objects.get(id=acolhimento_id)
    except Acolhimento.DoesNotExist:
        return None

    return dados_acolhimento_para_impressao(acolhimento)


def dados_acolhimento_para_impressao(acolhimento):
    data_acolhimento = (
        acolhimento.data_acolhimento.strftime("%d/%m/%Y %H:%M")
        if acolhimento.data_acolhimento
        else ""
    )

    return {
        "nome_paciente": acolhimento.nome_paciente or "",
        "cpf": acolhimento.cpf or "",
        "numero_bam": acolhimento.numero_bam or "",
        "data_nascimento": (
            acolhimento.data_nascimento.strftime("%d/%m/%Y")
            if acolhimento.data_nascimento
            else ""
        ),
        "idade": acolhimento.idade if acolhimento.idade is not None else "",
        "hora_chegada": (
            acolhimento.hora_chegada.strftime("%H:%M")
            if acolhimento.hora_chegada
            else ""
        ),
        "pressao_arterial": acolhimento.pressao_arterial or "",
        "temperatura": (
            str(acolhimento.temperatura).replace(".", ",")
            if acolhimento.temperatura is not None
            else ""
        ),
        "frequencia_respiratoria": (
            acolhimento.frequencia_respiratoria
            if acolhimento.frequencia_respiratoria is not None
            else ""
        ),
        "pulso": acolhimento.pulso if acolhimento.pulso is not None else "",
        "dor": acolhimento.dor if acolhimento.dor is not None else "",
        "tipo_atendimento": acolhimento.tipo_atendimento or "",
        "tipo_atendimento_label": acolhimento.get_tipo_atendimento_display(),
        "data_acolhimento": data_acolhimento,
    }


def buscar_historico_acolhimentos():
    inicio, fim = periodo_do_dia()

    return (
        Acolhimento.objects
        .filter(data_acolhimento__gte=inicio, data_acolhimento__lte=fim)
        .order_by("-data_acolhimento")
    )


def reenviar_para_recepcao(request, acolhimento_id):

    acolhimento = get_object_or_404(Acolhimento, id=acolhimento_id)

    acolhimento.reenviar_para_recepcao()

    messages.success(
        request,
        f"Atendimento BAM {acolhimento.numero_bam} reenviado para a recepção."
    )

    return redirect("tipo_atendimento")


# ==================================
# BUSCA AUTOMÁTICA AJAX
# ==================================

def buscar_paciente(request):

    busca = request.GET.get("busca", "").strip()

    pacientes = (
        Acolhimento.objects
        .filter(
            Q(nome_paciente__icontains=busca)
            | Q(cpf__icontains=busca)
        )
        .order_by("-id")
    )

    dados = []
    cpfs_adicionados = set()

    for paciente in pacientes:
        cpf = (paciente.cpf or "").strip()

        if cpf in cpfs_adicionados:
            continue

        cpfs_adicionados.add(cpf)

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
            "passagens_hoje": resumo_passagens_json(
                paciente,
                timezone.now()
            ),
        })

        if len(dados) >= 20:
            break

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
