from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.utils import (
    conselho_profissional_request,
    nome_profissional_request,
    registro_profissional_request,
)
from acolhimento.models import Acolhimento
from .forms import DadosTransporteAmbulanciaForm, SolicitacaoAmbulanciaForm
from .models import SolicitacaoAmbulancia


FILTROS_STATUS = [
    ("ativos", "Ativos", SolicitacaoAmbulancia.STATUS_ATIVOS),
    ("solicitados", "Solicitados", (SolicitacaoAmbulancia.SOLICITADO,)),
    ("preparo", "Em preparo", (SolicitacaoAmbulancia.PREPARANDO,)),
    ("transporte", "Aguardando/Saiu", (
        SolicitacaoAmbulancia.AGUARDANDO_TRANSPORTE,
        SolicitacaoAmbulancia.SAIU,
    )),
    ("concluidos", "Concluidos", (SolicitacaoAmbulancia.CONCLUIDO,)),
    ("cancelados", "Cancelados", (SolicitacaoAmbulancia.CANCELADO,)),
    ("todos", "Todos", None),
]
FILTROS_VALIDOS = {codigo for codigo, _rotulo, _status in FILTROS_STATUS}

ACOES_STATUS = [
    (SolicitacaoAmbulancia.PREPARANDO, "Preparar"),
    (SolicitacaoAmbulancia.AGUARDANDO_TRANSPORTE, "Aguardando"),
    (SolicitacaoAmbulancia.SAIU, "Saiu"),
    (SolicitacaoAmbulancia.CONCLUIDO, "Chegou"),
    (SolicitacaoAmbulancia.CANCELADO, "Cancelar"),
]
STATUS_VALIDOS = {status for status, _rotulo in SolicitacaoAmbulancia.STATUS_CHOICES}


def destino_pos_acao(request):
    destino = request.POST.get("next") or reverse("ambulancia_dashboard")

    if destino.startswith("?"):
        destino = f"{reverse('ambulancia_dashboard')}{destino}"

    return destino


def profissional_logado(request):
    return {
        "nome": nome_profissional_request(request),
        "conselho": conselho_profissional_request(request),
        "registro": registro_profissional_request(request),
    }


def pacientes_em_atendimento_json():
    limite = timezone.now() - timedelta(days=15)
    pacientes = (
        Acolhimento.objects
        .filter(data_acolhimento__gte=limite)
        .order_by("-data_acolhimento")[:120]
    )

    return {
        str(paciente.id): {
            "nome": paciente.nome_paciente or "",
            "bam": paciente.numero_bam or "",
            "cpf": paciente.cpf or "",
            "nascimento": paciente.data_nascimento.isoformat() if paciente.data_nascimento else "",
            "origem": paciente.get_status_display() or "Hospital",
        }
        for paciente in pacientes
    }


def contar_filtro(status):
    if status is None:
        return SolicitacaoAmbulancia.objects.count()

    return SolicitacaoAmbulancia.objects.filter(status__in=status).count()


def montar_filtros_status():
    return [
        {
            "codigo": codigo,
            "rotulo": rotulo,
            "total": contar_filtro(status),
        }
        for codigo, rotulo, status in FILTROS_STATUS
    ]


def aplicar_filtros(queryset, filtro_status, busca):
    if filtro_status not in FILTROS_VALIDOS:
        filtro_status = "ativos"

    for codigo, _rotulo, status in FILTROS_STATUS:
        if codigo == filtro_status and status:
            queryset = queryset.filter(status__in=status)
            break

    busca = (busca or "").strip()
    if busca:
        queryset = queryset.filter(
            Q(nome_paciente__icontains=busca)
            | Q(numero_bam__icontains=busca)
            | Q(cpf__icontains=busca)
            | Q(destino__icontains=busca)
            | Q(unidade_destino__icontains=busca)
        )

    return queryset, filtro_status, busca


@login_required
def dashboard(request):
    if request.method == "POST":
        form = SolicitacaoAmbulanciaForm(request.POST)

        if form.is_valid():
            solicitacao = form.save(commit=False)
            profissional = profissional_logado(request)
            solicitacao.solicitante = request.user
            solicitacao.profissional_solicitante = profissional["nome"]
            solicitacao.conselho_solicitante = profissional["conselho"]
            solicitacao.registro_solicitante = profissional["registro"]
            solicitacao.save()
            messages.success(request, "Solicitacao de ambulancia aberta com sucesso.")
            return redirect("ambulancia_dashboard")
    else:
        form = SolicitacaoAmbulanciaForm()

    filtro_status = request.GET.get("status", "ativos")
    busca = request.GET.get("q", "")
    solicitacoes = SolicitacaoAmbulancia.objects.select_related(
        "acolhimento",
        "solicitante",
    )
    solicitacoes, filtro_status, busca = aplicar_filtros(solicitacoes, filtro_status, busca)

    resumo_status = dict(
        SolicitacaoAmbulancia.objects.values("status").annotate(total=Count("id")).values_list("status", "total")
    )
    hoje_inicio = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    contexto = {
        "form": form,
        "solicitacoes": solicitacoes[:150],
        "filtros_status": montar_filtros_status(),
        "filtro_status": filtro_status,
        "busca": busca,
        "acoes_status": ACOES_STATUS,
        "status_solicitado": SolicitacaoAmbulancia.SOLICITADO,
        "status_concluido": SolicitacaoAmbulancia.CONCLUIDO,
        "status_cancelado": SolicitacaoAmbulancia.CANCELADO,
        "pacientes_data": pacientes_em_atendimento_json(),
        "total_ativos": SolicitacaoAmbulancia.objects.filter(
            status__in=SolicitacaoAmbulancia.STATUS_ATIVOS
        ).count(),
        "total_urgentes": SolicitacaoAmbulancia.objects.filter(
            status__in=SolicitacaoAmbulancia.STATUS_ATIVOS,
            prioridade__in=[
                SolicitacaoAmbulancia.URGENTE,
                SolicitacaoAmbulancia.EMERGENCIA,
            ],
        ).count(),
        "total_em_transporte": SolicitacaoAmbulancia.objects.filter(
            status=SolicitacaoAmbulancia.SAIU
        ).count(),
        "total_concluidos_hoje": SolicitacaoAmbulancia.objects.filter(
            status=SolicitacaoAmbulancia.CONCLUIDO,
            concluido_em__gte=hoje_inicio,
        ).count(),
        "resumo_status": resumo_status,
    }

    return render(request, "ambulancia/dashboard.html", contexto)


@login_required
@require_POST
def alterar_status(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoAmbulancia, id=solicitacao_id)
    novo_status = request.POST.get("status", "")

    if novo_status not in STATUS_VALIDOS:
        messages.error(request, "Status de ambulancia invalido.")
        return redirect("ambulancia_dashboard")

    profissional = profissional_logado(request)
    solicitacao.marcar_status(novo_status, profissional["nome"])

    campos = [
        "status",
        "status_atualizado_por",
        "atualizado_em",
        "preparo_em",
        "aguardando_transporte_em",
        "saida_em",
        "concluido_em",
        "cancelado_em",
    ]
    solicitacao.save(update_fields=campos)
    messages.success(
        request,
        f"Solicitacao #{solicitacao.id} atualizada para {solicitacao.get_status_display()}."
    )

    return redirect(destino_pos_acao(request))


@login_required
@require_POST
def atualizar_dados_transporte(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoAmbulancia, id=solicitacao_id)
    form = DadosTransporteAmbulanciaForm(request.POST, instance=solicitacao)

    if form.is_valid():
        form.save()
        messages.success(
            request,
            f"Dados da viagem #{solicitacao.id} atualizados com sucesso."
        )
    else:
        primeiro_erro = "Confira os dados da viagem."
        for erros in form.errors.values():
            if erros:
                primeiro_erro = erros[0]
                break

        messages.error(request, primeiro_erro)

    return redirect(destino_pos_acao(request))


@login_required
def imprimir_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoAmbulancia, id=solicitacao_id)

    return render(
        request,
        "ambulancia/imprimir.html",
        {
            "solicitacao": solicitacao,
            "profissional_impressao": nome_profissional_request(request),
            "data_impressao": timezone.now(),
        },
    )
