from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from acolhimento.models import Acolhimento
from acolhimento.tempos import anexar_entrada_setor
from acolhimento.utils import (
    anexar_passagens_do_dia,
    passagens_do_paciente_no_dia,
    periodo_do_dia,
)
from painel.models import ChamadaPainel
from painel.services import registrar_ausencia, registrar_chamada, registrar_retorno

from .forms import ClassificacaoForm
from .models import ClassificacaoRisco


def classificacao_dashboard(request):
    periodo_inicio, periodo_fim = periodo_do_dia(timezone.now())
    cache_passagens = {}
    dados_impressao = buscar_dados_impressao_classificacao(request)

    acolhimentos = (
        Acolhimento.objects
        .select_related("paciente")
        .prefetch_related("tempos_setores")
        .filter(
            status="CLASSIFICACAO",
            ausente_classificacao=False,
        )
        .order_by("data_acolhimento")
    )

    ausentes_classificacao = (
        Acolhimento.objects
        .select_related("paciente")
        .prefetch_related("tempos_setores")
        .filter(
            status="CLASSIFICACAO",
            ausente_classificacao=True,
        )
        .order_by("-data_ausente_classificacao", "data_acolhimento")
    )

    classificados_hoje = (
        ClassificacaoRisco.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .filter(
            data_classificacao__gte=periodo_inicio,
            data_classificacao__lte=periodo_fim,
            acolhimento__data_acolhimento__gte=periodo_inicio,
            acolhimento__data_acolhimento__lte=periodo_fim,
        )
        .order_by("-data_classificacao")
    )

    acolhimentos = anexar_entrada_setor(
        anexar_passagens_do_dia(acolhimentos, cache_passagens),
        "CLASSIFICACAO",
    )
    ausentes_classificacao = anexar_passagens_do_dia(
        ausentes_classificacao,
        cache_passagens,
    )

    return render(
        request,
        "classificacao/dashboard.html",
        {
            "acolhimentos": acolhimentos,
            "ausentes_classificacao": ausentes_classificacao,
            "total_ausentes_classificacao": len(ausentes_classificacao),
            "classificados_hoje": classificados_hoje,
            "total_classificados_hoje": classificados_hoje.count(),
            "periodo_classificacao_inicio": periodo_inicio,
            "periodo_classificacao_fim": periodo_fim,
            "dados_impressao_classificacao": dados_impressao,
        }
    )


def buscar_dados_impressao_classificacao(request):
    classificacao_id = request.session.pop("classificacao_impressao_id", None)

    if not classificacao_id:
        return None

    try:
        classificacao = (
            ClassificacaoRisco.objects
            .select_related("acolhimento", "acolhimento__paciente")
            .get(id=classificacao_id)
        )
    except ClassificacaoRisco.DoesNotExist:
        return None

    return dados_classificacao_para_impressao(classificacao)


def formatar_data(valor):
    return valor.strftime("%d/%m/%Y") if valor else ""


def formatar_data_hora(valor):
    return valor.strftime("%d/%m/%Y %H:%M") if valor else ""


def formatar_hora(valor):
    return valor.strftime("%H:%M") if valor else ""


def formatar_decimal(valor):
    if valor is None:
        return ""

    return str(valor).replace(".", ",")


def dados_classificacao_para_impressao(classificacao):
    acolhimento = classificacao.acolhimento
    paciente = acolhimento.paciente
    _, _, passagens_hospital_dia = passagens_do_paciente_no_dia(acolhimento)

    return {
        "bam": acolhimento.numero_bam or "",
        "paciente": (
            paciente.nome_completo
            if paciente
            else acolhimento.nome_paciente
        ),
        "cpf": (
            paciente.cpf
            if paciente and paciente.cpf
            else acolhimento.cpf or ""
        ),
        "nascimento": formatar_data(acolhimento.data_nascimento),
        "idade": acolhimento.idade if acolhimento.idade is not None else "",
        "tipo": acolhimento.get_tipo_atendimento_display(),
        "status": acolhimento.get_status_display(),
        "dataAcolhimento": formatar_data_hora(acolhimento.data_acolhimento),
        "horaChegada": (
            formatar_hora(acolhimento.hora_chegada)
            or formatar_hora(acolhimento.data_acolhimento)
        ),
        "pressao": acolhimento.pressao_arterial or "",
        "temperatura": formatar_decimal(acolhimento.temperatura),
        "fr": (
            acolhimento.frequencia_respiratoria
            if acolhimento.frequencia_respiratoria is not None
            else ""
        ),
        "pulso": acolhimento.pulso if acolhimento.pulso is not None else "",
        "dor": acolhimento.dor if acolhimento.dor is not None else "",
        "chamadas": f"{acolhimento.chamadas_classificacao}/4",
        "passagens": f"{passagens_hospital_dia.count()} hoje",
        "classificacao": classificacao.get_cor_display(),
        "queixa": classificacao.queixa_principal or "",
        "responsavel": classificacao.usuario_responsavel or "",
        "responsavelRegistro": classificacao.responsavel_registro or "",
        "horaClassificacao": formatar_data_hora(classificacao.data_classificacao),
        "formaChegada": classificacao.get_forma_chegada_display(),
        "tempoSintoma": classificacao.tempo_inicio_sintoma or "",
        "escalaDor": (
            classificacao.escala_dor
            if classificacao.escala_dor is not None
            else ""
        ),
        "possivelGravidez": (
            classificacao.get_possivel_gravidez_display()
            if classificacao.possivel_gravidez
            else ""
        ),
        "deficiencia": classificacao.deficiencia or "",
        "doencaPreExistente": classificacao.doenca_pre_existente or "",
        "alergia": classificacao.alergia or "",
        "usoMedicamento": classificacao.uso_medicamento or "",
        "glicemia": classificacao.glicemia if classificacao.glicemia is not None else "",
        "peso": formatar_decimal(classificacao.peso),
        "altura": formatar_decimal(classificacao.altura),
        "observacoes": classificacao.observacoes or "",
    }


def classificar_paciente(request, acolhimento_id):
    acolhimento = get_object_or_404(
        Acolhimento.objects.select_related("paciente"),
        id=acolhimento_id
    )

    periodo_inicio, periodo_fim, passagens_hospital_dia = passagens_do_paciente_no_dia(acolhimento)

    if request.method == "POST":
        form = ClassificacaoForm(request.POST)

        if form.is_valid():
            classificacao = form.save(commit=False)
            classificacao.acolhimento = acolhimento
            classificacao.save()

            acolhimento.status = "CONSULTA"
            acolhimento.ausente_classificacao = False
            acolhimento.data_ausente_classificacao = None
            acolhimento.status_antes_ausencia = ""
            acolhimento.data_ausente = None
            acolhimento.save(
                update_fields=[
                    "status",
                    "ausente_classificacao",
                    "data_ausente_classificacao",
                    "status_antes_ausencia",
                    "data_ausente",
                ]
            )

            request.session["classificacao_impressao_id"] = classificacao.id

            messages.success(
                request,
                f"Classificação registrada para o BAM {acolhimento.numero_bam}."
            )

            return redirect("classificacao_dashboard")

    else:
        form = ClassificacaoForm()

    return render(
        request,
        "classificacao/classificar.html",
        {
            "form": form,
            "acolhimento": acolhimento,
            "periodo_passagens_inicio": periodo_inicio,
            "periodo_passagens_fim": periodo_fim,
            "passagens_hospital_dia": passagens_hospital_dia,
            "total_passagens_hospital_dia": passagens_hospital_dia.count(),
            "tem_passagem_anterior_hoje": (
                passagens_hospital_dia
                .exclude(id=acolhimento.id)
                .exists()
            ),
        }
    )


def chamar_paciente_classificacao(request, acolhimento_id):
    if request.method != "POST":
        return redirect("classificacao_dashboard")

    acolhimento = get_object_or_404(
        Acolhimento,
        id=acolhimento_id,
        status="CLASSIFICACAO"
    )

    if acolhimento.chamadas_classificacao >= 4:
        messages.warning(
            request,
            f"BAM {acolhimento.numero_bam} ja foi chamado 4 vezes. Use Ausentar."
        )
        return redirect("classificacao_dashboard")

    acolhimento.chamadas_classificacao += 1
    acolhimento.data_ultima_chamada_classificacao = timezone.now()
    acolhimento.ausente_classificacao = False
    acolhimento.data_ausente_classificacao = None
    acolhimento.save(
        update_fields=[
            "chamadas_classificacao",
            "data_ultima_chamada_classificacao",
            "ausente_classificacao",
            "data_ausente_classificacao",
        ]
    )
    registrar_chamada(
        ChamadaPainel.CLASSIFICACAO,
        acolhimento,
        request,
        local_destino="Classificacao de risco",
    )

    messages.success(
        request,
        f"Chamada {acolhimento.chamadas_classificacao} registrada para o BAM {acolhimento.numero_bam}."
    )

    return redirect("classificacao_dashboard")


def ausentar_paciente_classificacao(request, acolhimento_id):
    if request.method != "POST":
        return redirect("classificacao_dashboard")

    acolhimento = get_object_or_404(
        Acolhimento,
        id=acolhimento_id,
        status="CLASSIFICACAO"
    )

    if acolhimento.chamadas_classificacao < 4:
        faltam = 4 - acolhimento.chamadas_classificacao
        messages.warning(
            request,
            f"Para ausentar o BAM {acolhimento.numero_bam}, registre mais {faltam} chamada(s)."
        )
        return redirect("classificacao_dashboard")

    if acolhimento.ausente_classificacao:
        messages.info(
            request,
            f"BAM {acolhimento.numero_bam} ja esta ausente na classificacao."
        )
        return redirect("classificacao_dashboard")

    agora = timezone.now()
    acolhimento.ausente_classificacao = True
    acolhimento.data_ausente_classificacao = agora
    acolhimento.status_antes_ausencia = "CLASSIFICACAO"
    acolhimento.data_ausente = agora
    acolhimento.save(
        update_fields=[
            "ausente_classificacao",
            "data_ausente_classificacao",
            "status_antes_ausencia",
            "data_ausente",
        ]
    )
    registrar_ausencia(
        ChamadaPainel.CLASSIFICACAO,
        acolhimento,
        request,
        local_destino="Classificacao de risco",
    )

    messages.warning(
        request,
        f"BAM {acolhimento.numero_bam} marcado como ausente na classificação."
    )

    return redirect("classificacao_dashboard")


def retornar_ausente_classificacao(request, acolhimento_id):
    if request.method != "POST":
        return redirect("classificacao_dashboard")

    acolhimento = get_object_or_404(
        Acolhimento,
        id=acolhimento_id,
        status="CLASSIFICACAO",
        ausente_classificacao=True,
    )

    registrar_retorno(
        ChamadaPainel.CLASSIFICACAO,
        acolhimento,
        request,
        local_destino="Classificacao de risco",
    )
    acolhimento.ausente_classificacao = False
    acolhimento.data_ausente_classificacao = None
    acolhimento.chamadas_classificacao = 0
    acolhimento.data_ultima_chamada_classificacao = None
    acolhimento.status_antes_ausencia = ""
    acolhimento.data_ausente = None
    acolhimento.save(
        update_fields=[
            "ausente_classificacao",
            "data_ausente_classificacao",
            "chamadas_classificacao",
            "data_ultima_chamada_classificacao",
            "status_antes_ausencia",
            "data_ausente",
        ]
    )

    messages.success(
        request,
        f"BAM {acolhimento.numero_bam} retornou para a fila da classificacao."
    )

    return redirect("classificacao_dashboard")
