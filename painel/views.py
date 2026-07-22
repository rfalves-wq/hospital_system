from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from .models import ChamadaPainel


def hora_chamada(valor):
    if not valor:
        return ""

    if timezone.is_aware(valor):
        valor = timezone.localtime(valor)

    return valor.strftime("%H:%M")


def chamada_payload(chamada):
    ausencia = chamada.tipo == ChamadaPainel.AUSENCIA

    return {
        "id": chamada.id,
        "tipo": chamada.tipo.lower(),
        "ausencia": ausencia,
        "setor": chamada.get_setor_display(),
        "titulo": "Paciente ausente" if ausencia else chamada.get_setor_display(),
        "historico": (
            f"Paciente ausente - {chamada.get_setor_display()}"
            if ausencia
            else chamada.get_setor_display()
        ),
        "setor_codigo": chamada.setor.lower(),
        "paciente": chamada.paciente_nome,
        "bam": chamada.numero_bam,
        "local": chamada.local_destino,
        "observacao": chamada.observacao,
        "hora": hora_chamada(chamada.criado_em),
    }


def chamadas_recentes():
    return (
        ChamadaPainel.objects
        .select_related("acolhimento")
        .filter(visivel_painel=True)
        .exclude(tipo=ChamadaPainel.RETORNO)[:12]
    )


def painel_chamados(request):
    chamadas = list(chamadas_recentes())

    return render(
        request,
        "painel/chamados.html",
        {
            "ultima_chamada": chamadas[0] if chamadas else None,
            "chamadas": chamadas,
        },
    )


def painel_chamados_dados(request):
    chamadas = list(chamadas_recentes())

    return JsonResponse(
        {
            "ultima": chamada_payload(chamadas[0]) if chamadas else None,
            "chamadas": [chamada_payload(chamada) for chamada in chamadas],
        }
    )
