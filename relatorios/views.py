import csv
from collections import defaultdict
from datetime import datetime, time, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date

from acolhimento.models import Acolhimento, PermanenciaSetorAtendimento
from acolhimento.tempos import formatar_duracao, somar_tempo_hospital
from almoxarifado.models import MaterialAlmoxarifado, MovimentacaoAlmoxarifado
from ambulancia.models import SolicitacaoAmbulancia
from auditoria.models import EventoAuditoria
from classificacao.models import ClassificacaoRisco
from farmacia.models import MedicamentoEstoque, MovimentacaoEstoque
from funcionarios.models import EscalaFuncionario, Funcionario
from medico.models import ConsultaMedica, ReavaliacaoMedica, TransferenciaConsultaMedica


def inicio_dia(data):
    return datetime.combine(data, time.min)


def fim_dia(data):
    return datetime.combine(data, time.max)


def periodo_request(request):
    hoje = timezone.now().date()
    inicio_param = parse_date(request.GET.get("inicio", ""))
    fim_param = parse_date(request.GET.get("fim", ""))

    if inicio_param or fim_param:
        data_inicio = inicio_param or fim_param or hoje
        data_fim = fim_param or inicio_param or hoje
    else:
        data_inicio = hoje - timedelta(days=6)
        data_fim = hoje

    if data_fim < data_inicio:
        data_inicio, data_fim = data_fim, data_inicio

    dias = (data_fim - data_inicio).days + 1

    return {
        "inicio_data": data_inicio,
        "fim_data": data_fim,
        "inicio_iso": data_inicio.isoformat(),
        "fim_iso": data_fim.isoformat(),
        "inicio": inicio_dia(data_inicio),
        "fim": fim_dia(data_fim),
        "dias": dias,
    }


def atalhos_periodo():
    hoje = timezone.now().date()
    return [
        {"rotulo": "Hoje", "inicio": hoje.isoformat(), "fim": hoje.isoformat()},
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


def rotulo_choice(choices, valor):
    return dict(choices).get(valor, valor or "-")


def percentual_valor(valor, maximo):
    if not maximo:
        return 0

    return max(4, round((valor / maximo) * 100)) if valor else 0


def adicionar_percentual_maximo(linhas, campo="total", destino="percentual_maximo"):
    maximo = max([item.get(campo) or 0 for item in linhas], default=0)

    for item in linhas:
        item[destino] = percentual_valor(item.get(campo) or 0, maximo)

    return linhas


def percentuais_grupo(queryset, campo, choices=None, limite=10):
    total = queryset.count()
    linhas = []

    for item in queryset.values(campo).annotate(total=Count("id")).order_by("-total", campo)[:limite]:
        valor = item[campo] or "-"
        linhas.append(
            {
                "rotulo": rotulo_choice(choices, valor) if choices else valor,
                "total": item["total"],
                "percentual": round((item["total"] / total) * 100) if total else 0,
            }
        )

    return linhas


def dias_periodo(periodo):
    dias = []
    data = periodo["inicio_data"]

    while data <= periodo["fim_data"]:
        dias.append(data)
        data += timedelta(days=1)

    return dias


def contagem_por_dia(queryset, campo_data):
    contagem = defaultdict(int)

    for valor in queryset.values_list(campo_data, flat=True):
        if not valor:
            continue

        data = valor.date() if hasattr(valor, "date") else valor
        contagem[data] += 1

    return contagem


def serie_operacional(periodo, acolhimentos, classificacoes, consultas, ambulancias):
    dias = dias_periodo(periodo)
    grupos = {
        "atendimentos": contagem_por_dia(acolhimentos, "data_acolhimento"),
        "classificacoes": contagem_por_dia(classificacoes, "data_classificacao"),
        "consultas": contagem_por_dia(consultas, "data_consulta"),
        "ambulancias": contagem_por_dia(ambulancias, "solicitado_em"),
    }
    maximo = max(
        [
            grupos[chave].get(dia, 0)
            for chave in grupos
            for dia in dias
        ],
        default=0,
    )
    serie = []

    for dia in dias:
        item = {
            "rotulo": dia.strftime("%d/%m"),
            "atendimentos": grupos["atendimentos"].get(dia, 0),
            "classificacoes": grupos["classificacoes"].get(dia, 0),
            "consultas": grupos["consultas"].get(dia, 0),
            "ambulancias": grupos["ambulancias"].get(dia, 0),
        }
        for chave in ["atendimentos", "classificacoes", "consultas", "ambulancias"]:
            item[f"{chave}_pct"] = percentual_valor(item[chave], maximo)
        serie.append(item)

    return {
        "dias": serie,
        "maximo": maximo,
    }


def top_por_campo(queryset, campo, rotulo, limite=8):
    linhas = []

    for item in (
        queryset
        .exclude(**{campo: ""})
        .values(campo)
        .annotate(total=Count("id"))
        .order_by("-total", campo)[:limite]
    ):
        linhas.append(
            {
                "profissional": item[campo] or "-",
                "setor": rotulo,
                "total": item["total"],
            }
        )

    return linhas


def top_soma_por_campo(queryset, campo, soma, limite=8):
    linhas = []

    for item in (
        queryset
        .exclude(**{campo: ""})
        .values(campo)
        .annotate(total=Sum(soma))
        .order_by("-total", campo)[:limite]
    ):
        linhas.append(
            {
                "rotulo": item[campo] or "-",
                "total": item["total"] or 0,
            }
        )

    return adicionar_percentual_maximo(linhas)


def producao_profissionais(periodo):
    inicio = periodo["inicio"]
    fim = periodo["fim"]
    linhas = []

    linhas.extend(
        top_por_campo(
            ClassificacaoRisco.objects.filter(data_classificacao__gte=inicio, data_classificacao__lte=fim),
            "usuario_responsavel",
            "Classificacao",
        )
    )
    linhas.extend(
        top_por_campo(
            ConsultaMedica.objects.filter(data_consulta__gte=inicio, data_consulta__lte=fim),
            "medico_responsavel",
            "Medico",
        )
    )
    linhas.extend(
        top_por_campo(
            ConsultaMedica.objects.filter(data_medicacao__gte=inicio, data_medicacao__lte=fim),
            "profissional_medicacao_nome",
            "Medicacao",
        )
    )
    linhas.extend(
        top_por_campo(
            ConsultaMedica.objects.filter(data_liberacao_farmacia__gte=inicio, data_liberacao_farmacia__lte=fim),
            "profissional_farmacia_nome",
            "Farmacia",
        )
    )
    linhas.extend(
        top_por_campo(
            ConsultaMedica.objects.filter(data_resultado_laboratorio__gte=inicio, data_resultado_laboratorio__lte=fim),
            "tecnico_laboratorio_nome",
            "Laboratorio",
        )
    )

    imagem_linhas = []
    for campo, data_campo, setor in [
        ("tecnico_raiox_nome", "data_resultado_raiox", "Raio-X"),
        ("tecnico_tomografia_nome", "data_resultado_tomografia", "Tomografia"),
        ("tecnico_mamografia_nome", "data_resultado_mamografia", "Mamografia"),
        ("tecnico_densitometria_nome", "data_resultado_densitometria", "Densitometria"),
    ]:
        filtros = {
            f"{data_campo}__gte": inicio,
            f"{data_campo}__lte": fim,
        }
        imagem_linhas.extend(top_por_campo(ConsultaMedica.objects.filter(**filtros), campo, setor, limite=5))

    linhas.extend(imagem_linhas)
    return adicionar_percentual_maximo(
        sorted(linhas, key=lambda item: item["total"], reverse=True)[:14]
    )


def tempos_por_setor(periodo):
    permanencias = PermanenciaSetorAtendimento.objects.filter(
        entrada__gte=periodo["inicio"],
        entrada__lte=periodo["fim"],
    ).exclude(setor="AUSENTE")

    grupos = defaultdict(lambda: {"total": timedelta(), "registros": 0, "abertos": 0})
    for permanencia in permanencias:
        grupos[permanencia.setor]["total"] += permanencia.duracao
        grupos[permanencia.setor]["registros"] += 1
        if permanencia.em_aberto:
            grupos[permanencia.setor]["abertos"] += 1

    escolhas = dict(PermanenciaSetorAtendimento.SETOR_CHOICES)
    linhas = []
    for setor, dados in grupos.items():
        media = dados["total"] / dados["registros"] if dados["registros"] else timedelta()
        linhas.append(
            {
                "setor": escolhas.get(setor, setor),
                "registros": dados["registros"],
                "abertos": dados["abertos"],
                "media": formatar_duracao(media),
                "total": formatar_duracao(dados["total"]),
                "minutos_media": int(media.total_seconds() // 60),
            }
        )

    linhas = sorted(linhas, key=lambda item: item["minutos_media"], reverse=True)[:12]
    return adicionar_percentual_maximo(linhas, campo="minutos_media", destino="percentual_media")


def tempo_medio_hospital(acolhimentos):
    total = timedelta()
    quantidade = 0

    for acolhimento in acolhimentos.prefetch_related("tempos_setores")[:1000]:
        duracao = somar_tempo_hospital(acolhimento.tempos_setores.all())
        if duracao:
            total += duracao
            quantidade += 1

    if not quantidade:
        return "0min"

    return formatar_duracao(total / quantidade)


def resumo_classificacao_ordenado(classificacoes):
    contagens = dict(
        classificacoes
        .values("cor")
        .annotate(total=Count("id"))
        .values_list("cor", "total")
    )
    ordem = [
        ("AZUL", "Azul - Nao urgente", "azul"),
        ("VERDE", "Verde - Pouco urgente", "verde"),
        ("AMARELO", "Amarelo - Urgente", "amarelo"),
        ("LARANJA", "Laranja - Muito urgente", "laranja"),
        ("VERMELHO", "Vermelho - Emergencia", "vermelho"),
    ]

    return [
        {
            "codigo": codigo,
            "rotulo": rotulo,
            "classe": classe,
            "total": contagens.get(codigo, 0),
        }
        for codigo, rotulo, classe in ordem
    ]


def triagens_ultima_semana(hoje):
    inicio_semana = inicio_dia(hoje - timedelta(days=6))
    fim_semana = fim_dia(hoje)
    linhas = []
    triagens = (
        ClassificacaoRisco.objects
        .filter(data_classificacao__gte=inicio_semana, data_classificacao__lte=fim_semana)
        .select_related("acolhimento")
        .order_by("-data_classificacao")[:10]
    )

    for triagem in triagens:
        acolhimento = triagem.acolhimento
        linhas.append(
            {
                "paciente": acolhimento.nome_paciente,
                "bam": acolhimento.numero_bam or "-",
                "chegada": triagem.data_classificacao,
                "risco": rotulo_choice(ClassificacaoRisco.COR_CHOICES, triagem.cor),
                "risco_classe": (triagem.cor or "").lower(),
                "usuario": triagem.usuario_responsavel or "-",
            }
        )

    return linhas


def pacientes_recorrentes(acolhimentos):
    return list(
        acolhimentos
        .exclude(cpf__isnull=True)
        .exclude(cpf="")
        .values("cpf", "nome_paciente")
        .annotate(total=Count("id"))
        .filter(total__gt=1)
        .order_by("-total", "nome_paciente")[:12]
    )


def relatorio_contexto(request):
    periodo = periodo_request(request)
    inicio = periodo["inicio"]
    fim = periodo["fim"]
    hoje = timezone.now().date()

    acolhimentos = Acolhimento.objects.filter(data_acolhimento__gte=inicio, data_acolhimento__lte=fim)
    classificacoes = ClassificacaoRisco.objects.filter(data_classificacao__gte=inicio, data_classificacao__lte=fim)
    consultas = ConsultaMedica.objects.filter(data_consulta__gte=inicio, data_consulta__lte=fim)
    ambulancias = SolicitacaoAmbulancia.objects.filter(solicitado_em__gte=inicio, solicitado_em__lte=fim)
    auditoria = EventoAuditoria.objects.filter(criado_em__gte=inicio, criado_em__lte=fim)
    movimentacoes = MovimentacaoEstoque.objects.filter(criado_em__gte=inicio, criado_em__lte=fim)
    movimentacoes_almoxarifado = MovimentacaoAlmoxarifado.objects.filter(criado_em__gte=inicio, criado_em__lte=fim)

    pendencias = {
        "medicacao": ConsultaMedica.objects.filter(solicita_medicacao=True, medicacao_realizada=False).count(),
        "laboratorio": ConsultaMedica.objects.filter(
            solicita_exames_laboratoriais=True,
            exames_laboratoriais_realizados=False,
        ).count(),
        "imagem": ConsultaMedica.objects.filter(
            solicita_exames_imagem=True,
            exames_imagem_realizados=False,
        ).count(),
        "ambulancia": SolicitacaoAmbulancia.objects.filter(
            status__in=SolicitacaoAmbulancia.STATUS_ATIVOS,
        ).count(),
    }

    km_ambulancia = sum(
        solicitacao.km_percorrido or 0
        for solicitacao in ambulancias
    )
    estoque_baixo = MedicamentoEstoque.objects.filter(
        ativo=True,
        estoque_atual__lte=F("estoque_minimo"),
    ).count()
    top_cids = list(
        consultas
        .exclude(cid="")
        .values("cid")
        .annotate(total=Count("id"))
        .order_by("-total", "cid")[:8]
    )
    adicionar_percentual_maximo(top_cids)
    funcionarios_ativos = Funcionario.objects.filter(ativo=True)
    funcionarios_setor = percentuais_grupo(
        funcionarios_ativos,
        "setor",
        Funcionario.SETOR_CHOICES,
        limite=10,
    )
    funcionarios_cargo = adicionar_percentual_maximo(
        [
            {"rotulo": item["cargo"] or "-", "total": item["total"]}
            for item in (
                funcionarios_ativos
                .exclude(cargo="")
                .values("cargo")
                .annotate(total=Count("id"))
                .order_by("-total", "cargo")[:8]
            )
        ]
    )
    estoque_saida = movimentacoes.filter(tipo=MovimentacaoEstoque.SAIDA)
    estoque_saida_almoxarifado = movimentacoes_almoxarifado.filter(tipo=MovimentacaoAlmoxarifado.SAIDA)
    status_abertos = ["RECEPCAO", "CLASSIFICACAO", "CONSULTA", "PROCEDIMENTOS", "RETORNO_MEDICO", "OBSERVACAO", "INTERNACAO"]
    situacao_atual = {
        "triagem": Acolhimento.objects.filter(status="CLASSIFICACAO").count(),
        "recepcao": Acolhimento.objects.filter(status="RECEPCAO").count(),
        "fila_medica": Acolhimento.objects.filter(status__in=["CONSULTA", "RETORNO_MEDICO"]).count(),
        "internacao": Acolhimento.objects.filter(status="INTERNACAO").count(),
    }

    contexto = {
        "periodo": periodo,
        "atalhos_periodo": atalhos_periodo(),
        "dashboard_operacional": [
            {
                "rotulo": f"Classificacoes no periodo ({periodo['dias']} dias)",
                "valor": classificacoes.count(),
                "classe": "azul",
            },
            {
                "rotulo": f"Classificacoes do fluxo ambulatorial ({periodo['dias']} dias)",
                "valor": acolhimentos.count(),
                "classe": "verde",
            },
            {
                "rotulo": "Boletins em aberto agora",
                "valor": Acolhimento.objects.filter(status__in=status_abertos).count(),
                "classe": "amarelo",
            },
            {
                "rotulo": f"Agendamentos ({periodo['dias']} dias)",
                "valor": 0,
                "classe": "cinza",
            },
        ],
        "situacao_atual": [
            {"rotulo": "Senhas aguardando triagem", "valor": situacao_atual["triagem"], "classe": "azul"},
            {"rotulo": "Pacientes aguardando recepcao", "valor": situacao_atual["recepcao"], "classe": "verde"},
            {"rotulo": "Pacientes na fila medica", "valor": situacao_atual["fila_medica"], "classe": "amarelo"},
            {"rotulo": "Internacoes pendentes", "valor": situacao_atual["internacao"], "classe": "cinza"},
        ],
        "classificacao_resumo": resumo_classificacao_ordenado(classificacoes),
        "triagens_semana": triagens_ultima_semana(hoje),
        "agenda_semana": [],
        "pacientes_recorrentes": pacientes_recorrentes(acolhimentos),
        "serie_operacional": serie_operacional(
            periodo,
            acolhimentos,
            classificacoes,
            consultas,
            ambulancias,
        ),
        "cards": [
            {"rotulo": "Atendimentos", "valor": acolhimentos.count(), "classe": "atendimentos"},
            {"rotulo": "Finalizados", "valor": acolhimentos.filter(status="FINALIZADO").count(), "classe": "finalizados"},
            {"rotulo": "Consultas medicas", "valor": consultas.count(), "classe": "consultas"},
            {"rotulo": "Tempo medio", "valor": tempo_medio_hospital(acolhimentos), "classe": "tempo"},
            {"rotulo": "Pendencias", "valor": sum(pendencias.values()), "classe": "pendencias"},
            {"rotulo": "Alertas auditoria", "valor": auditoria.filter(Q(status_code__gte=400) | Q(acao__in=[EventoAuditoria.ERRO, EventoAuditoria.ACESSO_NEGADO, EventoAuditoria.FALHA_LOGIN])).count(), "classe": "alertas"},
        ],
        "status_atendimento": percentuais_grupo(acolhimentos, "status", Acolhimento.STATUS_CHOICES),
        "classificacao_risco": percentuais_grupo(classificacoes, "cor", ClassificacaoRisco.COR_CHOICES),
        "condutas_medicas": percentuais_grupo(consultas, "conduta", ConsultaMedica.CONDUTA_CHOICES),
        "tempos_setores": tempos_por_setor(periodo),
        "producao_profissionais": producao_profissionais(periodo),
        "procedimentos_medicos": {
            "medicacao_solicitada": consultas.filter(solicita_medicacao=True).count(),
            "medicacao_realizada": consultas.filter(
                solicita_medicacao=True,
                medicacao_realizada=True,
            ).count(),
            "laboratorio_solicitado": consultas.filter(solicita_exames_laboratoriais=True).count(),
            "laboratorio_realizado": consultas.filter(
                solicita_exames_laboratoriais=True,
                exames_laboratoriais_realizados=True,
            ).count(),
            "imagem_solicitada": consultas.filter(solicita_exames_imagem=True).count(),
            "imagem_realizada": consultas.filter(
                solicita_exames_imagem=True,
                exames_imagem_realizados=True,
            ).count(),
        },
        "pendencias": pendencias,
        "ambulancia": {
            "total": ambulancias.count(),
            "ativas": ambulancias.filter(status__in=SolicitacaoAmbulancia.STATUS_ATIVOS).count(),
            "concluidas": ambulancias.filter(status=SolicitacaoAmbulancia.CONCLUIDO).count(),
            "canceladas": ambulancias.filter(status=SolicitacaoAmbulancia.CANCELADO).count(),
            "km": km_ambulancia,
        },
        "ambulancia_status": percentuais_grupo(
            ambulancias,
            "status",
            SolicitacaoAmbulancia.STATUS_CHOICES,
        ),
        "ambulancia_tipo": percentuais_grupo(
            ambulancias,
            "tipo_transporte",
            SolicitacaoAmbulancia.TIPO_CHOICES,
        ),
        "ambulancia_prioridade": percentuais_grupo(
            ambulancias,
            "prioridade",
            SolicitacaoAmbulancia.PRIORIDADE_CHOICES,
        ),
        "farmacia": {
            "estoque_baixo": estoque_baixo,
            "vencidos": MedicamentoEstoque.objects.filter(ativo=True, validade__lt=hoje).count(),
            "entradas": movimentacoes.filter(tipo=MovimentacaoEstoque.ENTRADA).count(),
            "saidas": movimentacoes.filter(tipo=MovimentacaoEstoque.SAIDA).count(),
            "quantidade_entrada": movimentacoes.filter(
                tipo=MovimentacaoEstoque.ENTRADA,
            ).aggregate(total=Sum("quantidade"))["total"] or 0,
            "quantidade_saida": estoque_saida.aggregate(total=Sum("quantidade"))["total"] or 0,
        },
        "farmacia_movimentacao": percentuais_grupo(
            movimentacoes,
            "tipo",
            MovimentacaoEstoque.TIPO_CHOICES,
        ),
        "farmacia_top_saidas": top_soma_por_campo(
            estoque_saida,
            "medicamento__nome",
            "quantidade",
        ),
        "almoxarifado": {
            "materiais_ativos": MaterialAlmoxarifado.objects.filter(ativo=True).count(),
            "estoque_baixo": MaterialAlmoxarifado.objects.filter(
                ativo=True,
                estoque_atual__lte=F("estoque_minimo"),
            ).count(),
            "zerados": MaterialAlmoxarifado.objects.filter(ativo=True, estoque_atual__lte=0).count(),
            "entradas": movimentacoes_almoxarifado.filter(tipo=MovimentacaoAlmoxarifado.ENTRADA).count(),
            "saidas": estoque_saida_almoxarifado.count(),
            "quantidade_saida": estoque_saida_almoxarifado.aggregate(total=Sum("quantidade"))["total"] or 0,
        },
        "almoxarifado_top_saidas": top_soma_por_campo(
            estoque_saida_almoxarifado,
            "material__nome",
            "quantidade",
        ),
        "funcionarios": {
            "ativos": funcionarios_ativos.count(),
            "inativos": Funcionario.objects.filter(ativo=False).count(),
            "sem_conselho": funcionarios_ativos.filter(
                Q(conselho_profissional="") | Q(registro_profissional="")
            ).count(),
            "escala_hoje": EscalaFuncionario.objects.filter(data=hoje).exclude(
                status=EscalaFuncionario.CANCELADA,
            ).count(),
        },
        "funcionarios_setor": funcionarios_setor,
        "funcionarios_cargo": funcionarios_cargo,
        "auditoria": percentuais_grupo(auditoria, "acao", EventoAuditoria.ACAO_CHOICES, limite=8),
        "auditoria_modulos": percentuais_grupo(auditoria, "modulo", limite=8),
        "auditoria_http": {
            "sucesso": auditoria.filter(status_code__gte=200, status_code__lt=300).count(),
            "redirecionamento": auditoria.filter(status_code__gte=300, status_code__lt=400).count(),
            "erro": auditoria.filter(status_code__gte=400).count(),
            "sem_status": auditoria.filter(status_code__isnull=True).count(),
        },
        "top_cids": top_cids,
        "transferencias_medicas": TransferenciaConsultaMedica.objects.filter(
            data_transferencia__gte=inicio,
            data_transferencia__lte=fim,
        ).count(),
        "reavaliacoes_medicas": ReavaliacaoMedica.objects.filter(
            data_reavaliacao__gte=inicio,
            data_reavaliacao__lte=fim,
        ).count(),
    }

    return contexto


@login_required
def dashboard(request):
    return render(request, "relatorios/dashboard.html", relatorio_contexto(request))


@login_required
def exportar_csv(request):
    contexto = relatorio_contexto(request)
    periodo = contexto["periodo"]
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    nome_arquivo = timezone.now().strftime("relatorios_%Y%m%d_%H%M%S.csv")
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Relatorio", "Inicio", periodo["inicio_data"].strftime("%d/%m/%Y")])
    writer.writerow(["Relatorio", "Fim", periodo["fim_data"].strftime("%d/%m/%Y")])
    writer.writerow([])
    writer.writerow(["Indicador", "Valor"])

    for card in contexto["cards"]:
        writer.writerow([card["rotulo"], card["valor"]])

    writer.writerow([])
    writer.writerow(["Pendencia", "Total"])
    for chave, valor in contexto["pendencias"].items():
        writer.writerow([chave, valor])

    writer.writerow([])
    writer.writerow(["Setor", "Registros", "Abertos", "Media", "Total"])
    for item in contexto["tempos_setores"]:
        writer.writerow([item["setor"], item["registros"], item["abertos"], item["media"], item["total"]])

    writer.writerow([])
    writer.writerow(["Profissional", "Setor", "Total"])
    for item in contexto["producao_profissionais"]:
        writer.writerow([item["profissional"], item["setor"], item["total"]])

    return response
