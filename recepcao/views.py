import json
from datetime import date
from urllib import error as urlerror
from urllib import request as urlrequest

from django.contrib import messages
from django.core.cache import cache
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from acolhimento.models import Acolhimento
from acolhimento.utils import anexar_passagens_do_dia, passagens_do_paciente_no_dia
from painel.models import ChamadaPainel
from painel.services import (
    anexar_status_chamadas,
    marcar_acolhimento_ausente,
    registrar_ausencia,
    registrar_chamada_limitada,
    registrar_retorno,
    reativar_acolhimento_ausente,
    total_chamadas_setor,
)

from .forms import RecepcaoForm
from .models import Recepcao


CIDADES_CACHE_TIMEOUT = 60 * 60 * 24
IBGE_MUNICIPIOS_URL = (
    "https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
)


def cidades_por_uf(request, uf):
    uf_normalizada = (uf or "").strip().upper()
    ufs_validas = {codigo for codigo, _nome in Recepcao.UF_CHOICES}

    if uf_normalizada not in ufs_validas:
        return JsonResponse({"erro": "UF invalida."}, status=400)

    cache_key = f"recepcao:cidades:{uf_normalizada}"
    cidades = cache.get(cache_key)

    if cidades is not None:
        return JsonResponse(cidades, safe=False)

    try:
        with urlrequest.urlopen(
            IBGE_MUNICIPIOS_URL.format(uf=uf_normalizada),
            timeout=8
        ) as resposta:
            if resposta.status != 200:
                return JsonResponse(
                    {"erro": "Nao foi possivel consultar as cidades."}
                )

            dados = json.loads(resposta.read().decode("utf-8"))
    except (TimeoutError, OSError, urlerror.URLError, json.JSONDecodeError):
        return JsonResponse(
            {"erro": "Nao foi possivel consultar as cidades."}
        )

    cidades = [
        {"nome": cidade["nome"]}
        for cidade in dados
        if isinstance(cidade, dict) and cidade.get("nome")
    ]
    cidades.sort(key=lambda cidade: cidade["nome"])

    cache.set(cache_key, cidades, CIDADES_CACHE_TIMEOUT)

    return JsonResponse(cidades, safe=False)


def recepcao_dashboard(request):
    hoje = date.today()
    dados_impressao = buscar_dados_impressao_recepcao(request)

    acolhimentos = (
        Acolhimento.objects
        .select_related("paciente")
        .filter(
            data_acolhimento__date=hoje,
            status="RECEPCAO"
        )
        .order_by("-data_acolhimento")
    )

    historico = (
        Acolhimento.objects
        .select_related("paciente")
        .filter(data_acolhimento__date=hoje)
        .exclude(status__in=["RECEPCAO", "AUSENTE"])
        .order_by("-data_acolhimento")
    )

    ausentes_recepcao = (
        Acolhimento.objects
        .select_related("paciente")
        .filter(
            data_acolhimento__date=hoje,
            status="AUSENTE",
        )
        .filter(
            Q(status_antes_ausencia="RECEPCAO")
            | Q(
                status_antes_ausencia="",
                chamadas_painel__setor=ChamadaPainel.RECEPCAO,
                chamadas_painel__tipo=ChamadaPainel.AUSENCIA,
            )
        )
        .distinct()
        .order_by("-data_ausente", "-data_acolhimento")
    )

    acolhimentos = anexar_passagens_do_dia(acolhimentos)
    anexar_status_chamadas(acolhimentos, ChamadaPainel.RECEPCAO)

    return render(
        request,
        "recepcao/dashboard.html",
        {
            "acolhimentos": acolhimentos,
            "historico": anexar_passagens_do_dia(historico),
            "ausentes_recepcao": anexar_passagens_do_dia(ausentes_recepcao),
            "dados_impressao_recepcao": dados_impressao,
        }
    )


def buscar_dados_impressao_recepcao(request):
    acolhimento_id = request.session.pop("recepcao_impressao_acolhimento_id", None)

    if not acolhimento_id:
        return None

    try:
        acolhimento = (
            Acolhimento.objects
            .select_related("paciente")
            .get(id=acolhimento_id)
        )
    except Acolhimento.DoesNotExist:
        return None

    if not acolhimento.paciente:
        return None

    return dados_recepcao_para_impressao(acolhimento)


def texto_sim_nao(valor):
    return "Sim" if valor else "Nao"


def formatar_data(valor):
    return valor.strftime("%d/%m/%Y") if valor else ""


def formatar_data_hora(valor):
    return valor.strftime("%d/%m/%Y %H:%M") if valor else ""


def formatar_hora(valor):
    return valor.strftime("%H:%M") if valor else ""


def dados_recepcao_para_impressao(acolhimento):
    paciente = acolhimento.paciente

    return {
        "numero_bam": acolhimento.numero_bam or "",
        "data_acolhimento": formatar_data_hora(acolhimento.data_acolhimento),
        "hora_chegada": (
            formatar_hora(acolhimento.hora_chegada)
            or formatar_hora(acolhimento.data_acolhimento)
        ),
        "tipo_atendimento": acolhimento.get_tipo_atendimento_display(),
        "status": acolhimento.get_status_display(),
        "data_recepcao": formatar_data_hora(paciente.data_atualizacao),
        "nome_completo": paciente.nome_completo or "",
        "nome_social": paciente.nome_social or "",
        "cpf": paciente.cpf or "",
        "cns": paciente.cns or "",
        "sexo": paciente.get_sexo_display(),
        "raca_cor": paciente.get_raca_cor_display(),
        "nascimento": formatar_data(paciente.nascimento),
        "idade": paciente.idade if paciente.idade is not None else "",
        "nacionalidade": paciente.get_nacionalidade_display(),
        "uf_nascimento": paciente.uf_nascimento or "",
        "naturalidade": paciente.naturalidade or "",
        "situacao_rua": texto_sim_nao(paciente.situacao_rua),
        "nome_mae": paciente.nome_mae or "",
        "nome_pai": paciente.nome_pai or "",
        "telefone": paciente.telefone or "",
        "email": paciente.email or "",
        "cep": paciente.cep or "",
        "municipio": paciente.municipio or "",
        "bairro": paciente.bairro or "",
        "logradouro": paciente.logradouro or "",
        "numero": paciente.numero or "",
        "complemento": paciente.complemento or "",
        "nome_responsavel": paciente.nome_responsavel or "",
        "cpf_responsavel": paciente.cpf_responsavel or "",
        "nacionalidade_responsavel": paciente.nacionalidade_responsavel or "",
        "uf_nascimento_responsavel": paciente.uf_nascimento_responsavel or "",
        "naturalidade_responsavel": paciente.naturalidade_responsavel or "",
    }


def cadastrar_paciente(request, acolhimento_id):
    acolhimento = get_object_or_404(
        Acolhimento.objects.select_related("paciente"),
        id=acolhimento_id
    )

    paciente_existente = Recepcao.objects.filter(cpf=acolhimento.cpf).first()
    periodo_inicio, periodo_fim, passagens_hospital_dia = passagens_do_paciente_no_dia(acolhimento)

    if request.method == "POST":

        if paciente_existente:
            form = RecepcaoForm(request.POST, instance=paciente_existente)
        else:
            form = RecepcaoForm(request.POST)

        if form.is_valid():
            paciente = form.save()

            acolhimento.paciente = paciente
            acolhimento.status = "CLASSIFICACAO"
            acolhimento.save()

            request.session["recepcao_impressao_acolhimento_id"] = acolhimento.id

            messages.success(
                request,
                f"Paciente {paciente.nome_completo} salvo e encaminhado para a Classificação de Risco."
            )

            return redirect("recepcao_dashboard")

    else:

        if paciente_existente:
            form = RecepcaoForm(instance=paciente_existente)
        else:
            form = RecepcaoForm(
                initial={
                    "nome_completo": acolhimento.nome_paciente,
                    "cpf": acolhimento.cpf,
                    "nascimento": acolhimento.data_nascimento,
                    "idade": acolhimento.idade,
                }
            )

    return render(
        request,
        "recepcao/cadastro.html",
        {
            "form": form,
            "acolhimento": acolhimento,
            "paciente_existente": paciente_existente,
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


def enviar_classificacao(request, acolhimento_id):
    acolhimento = get_object_or_404(Acolhimento, id=acolhimento_id)

    if acolhimento.paciente:
        acolhimento.status = "CLASSIFICACAO"
        acolhimento.save()
        request.session["recepcao_impressao_acolhimento_id"] = acolhimento.id

    return redirect("recepcao_dashboard")


def chamar_paciente_recepcao(request, acolhimento_id):
    if request.method != "POST":
        return redirect("recepcao_dashboard")

    acolhimento = get_object_or_404(
        Acolhimento.objects.select_related("paciente"),
        id=acolhimento_id,
        status="RECEPCAO",
    )
    chamada, total = registrar_chamada_limitada(
        ChamadaPainel.RECEPCAO,
        acolhimento,
        request,
        local_destino="Recepcao",
    )

    if not chamada:
        messages.warning(
            request,
            f"BAM {acolhimento.numero_bam} ja foi chamado 4 vezes. Use Ausentar."
        )
        return redirect("recepcao_dashboard")

    messages.success(
        request,
        f"Chamada {total}/4 registrada para o BAM {acolhimento.numero_bam} na recepcao."
    )

    return redirect("recepcao_dashboard")


def ausentar_paciente_recepcao(request, acolhimento_id):
    if request.method != "POST":
        return redirect("recepcao_dashboard")

    acolhimento = get_object_or_404(
        Acolhimento.objects.select_related("paciente"),
        id=acolhimento_id,
        status="RECEPCAO",
    )
    total = total_chamadas_setor(ChamadaPainel.RECEPCAO, acolhimento)

    if total < 4:
        faltam = 4 - total
        messages.warning(
            request,
            f"Para ausentar o BAM {acolhimento.numero_bam}, registre mais {faltam} chamada(s)."
        )
        return redirect("recepcao_dashboard")

    registrar_ausencia(
        ChamadaPainel.RECEPCAO,
        acolhimento,
        request,
        local_destino="Recepcao",
    )
    marcar_acolhimento_ausente(acolhimento)

    messages.warning(
        request,
        f"BAM {acolhimento.numero_bam} marcado como ausente na recepcao."
    )

    return redirect("recepcao_dashboard")


def retornar_ausente_recepcao(request, acolhimento_id):
    if request.method != "POST":
        return redirect("recepcao_dashboard")

    acolhimento = get_object_or_404(
        Acolhimento.objects.select_related("paciente"),
        id=acolhimento_id,
        status="AUSENTE",
    )
    status_retorno = acolhimento.status_antes_ausencia or "RECEPCAO"

    if status_retorno != "RECEPCAO":
        messages.warning(
            request,
            f"BAM {acolhimento.numero_bam} esta ausente em outro setor."
        )
        return redirect("recepcao_dashboard")

    registrar_retorno(
        ChamadaPainel.RECEPCAO,
        acolhimento,
        request,
        local_destino="Recepcao",
    )
    reativar_acolhimento_ausente(acolhimento, "RECEPCAO")

    messages.success(
        request,
        f"BAM {acolhimento.numero_bam} retornou para a fila da recepcao."
    )

    return redirect("recepcao_dashboard")
