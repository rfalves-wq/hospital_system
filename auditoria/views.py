import csv
import json
from datetime import datetime, time, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date

from .models import EventoAuditoria


def inicio_dia(data):
    return datetime.combine(data, time.min)


def fim_dia(data):
    return datetime.combine(data, time.max)


def aplicar_filtros(eventos, filtros):
    busca = filtros.get("q", "").strip()
    acao = filtros.get("acao", "").strip()
    modulo = filtros.get("modulo", "").strip()
    data_inicio = parse_date(filtros.get("inicio", ""))
    data_fim = parse_date(filtros.get("fim", ""))

    if busca:
        eventos = eventos.filter(
            Q(profissional__icontains=busca)
            | Q(usuario_login__icontains=busca)
            | Q(nome_paciente__icontains=busca)
            | Q(numero_bam__icontains=busca)
            | Q(caminho__icontains=busca)
            | Q(descricao__icontains=busca)
            | Q(objeto_id__icontains=busca)
        )

    if acao:
        eventos = eventos.filter(acao=acao)

    if modulo:
        eventos = eventos.filter(modulo=modulo)

    if data_inicio:
        eventos = eventos.filter(criado_em__gte=inicio_dia(data_inicio))

    if data_fim:
        eventos = eventos.filter(criado_em__lte=fim_dia(data_fim))

    return eventos


def rotulo_acao(acao):
    return dict(EventoAuditoria.ACAO_CHOICES).get(acao, acao)


def query_resumo_por_campo(eventos, campo, limite=8):
    return (
        eventos
        .exclude(**{campo: ""})
        .values(campo)
        .annotate(total=Count("id"))
        .order_by("-total", campo)[:limite]
    )


def atalhos_periodo():
    hoje = timezone.now().date()
    return [
        {
            "rotulo": "Hoje",
            "inicio": hoje.isoformat(),
            "fim": hoje.isoformat(),
        },
        {
            "rotulo": "7 dias",
            "inicio": (hoje - timedelta(days=6)).isoformat(),
            "fim": hoje.isoformat(),
        },
        {
            "rotulo": "30 dias",
            "inicio": (hoje - timedelta(days=29)).isoformat(),
            "fim": hoje.isoformat(),
        },
    ]


@login_required
def dashboard(request):
    eventos_base = EventoAuditoria.objects.select_related("usuario")
    eventos = aplicar_filtros(eventos_base, request.GET)

    hoje_inicio = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    totais_por_acao = dict(
        EventoAuditoria.objects.values("acao").annotate(total=Count("id")).values_list("acao", "total")
    )
    modulos = (
        EventoAuditoria.objects
        .exclude(modulo="")
        .order_by("modulo")
        .values_list("modulo", flat=True)
        .distinct()
    )
    acoes_resumo = [
        {
            "acao": item["acao"],
            "rotulo": rotulo_acao(item["acao"]),
            "total": item["total"],
        }
        for item in eventos.values("acao").annotate(total=Count("id")).order_by("-total", "acao")[:8]
    ]

    contexto = {
        "eventos": eventos[:300],
        "total_filtrado": eventos.count(),
        "total_hoje": EventoAuditoria.objects.filter(criado_em__gte=hoje_inicio).count(),
        "total_gravacoes": totais_por_acao.get(EventoAuditoria.GRAVACAO, 0),
        "total_impressoes": totais_por_acao.get(EventoAuditoria.IMPRESSAO, 0),
        "total_erros": EventoAuditoria.objects.filter(status_code__gte=400).count(),
        "acoes": EventoAuditoria.ACAO_CHOICES,
        "modulos": modulos,
        "acoes_resumo": acoes_resumo,
        "modulos_resumo": query_resumo_por_campo(eventos, "modulo"),
        "profissionais_resumo": query_resumo_por_campo(eventos, "profissional", limite=6),
        "eventos_criticos": eventos.filter(
            Q(status_code__gte=400)
            | Q(acao__in=[
                EventoAuditoria.FALHA_LOGIN,
                EventoAuditoria.ACESSO_NEGADO,
                EventoAuditoria.ERRO,
            ])
        )[:8],
        "atalhos_periodo": atalhos_periodo(),
        "filtros": {
            "q": request.GET.get("q", ""),
            "acao": request.GET.get("acao", ""),
            "modulo": request.GET.get("modulo", ""),
            "inicio": request.GET.get("inicio", ""),
            "fim": request.GET.get("fim", ""),
        },
    }

    return render(request, "auditoria/dashboard.html", contexto)


@login_required
def exportar_csv(request):
    eventos = aplicar_filtros(
        EventoAuditoria.objects.select_related("usuario"),
        request.GET,
    )
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    nome_arquivo = timezone.now().strftime("auditoria_%Y%m%d_%H%M%S.csv")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    writer.writerow(
        [
            "Data/Hora",
            "Acao",
            "Modulo",
            "Profissional",
            "Usuario",
            "Conselho",
            "Registro",
            "Paciente",
            "BAM",
            "Descricao",
            "Metodo",
            "Status HTTP",
            "Caminho",
            "IP",
            "Objeto",
            "Dados",
        ]
    )

    for evento in eventos[:5000]:
        writer.writerow(
            [
                evento.criado_em.strftime("%d/%m/%Y %H:%M:%S"),
                evento.get_acao_display(),
                evento.modulo,
                evento.profissional,
                evento.usuario_login,
                evento.conselho,
                evento.registro,
                evento.nome_paciente,
                evento.numero_bam,
                evento.descricao,
                evento.metodo,
                evento.status_code or "",
                evento.caminho,
                evento.ip or "",
                f"{evento.objeto_tipo} #{evento.objeto_id}".strip(),
                json.dumps(evento.dados, ensure_ascii=False),
            ]
        )

    return response
