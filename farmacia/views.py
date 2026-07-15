from datetime import date, datetime, timedelta

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils import timezone

from medico.models import ConsultaMedica

from .forms import FarmaciaForm, MedicamentoEstoqueForm, MovimentacaoEstoqueForm
from .models import MedicamentoEstoque, MovimentacaoEstoque


TIPOS_MOVIMENTACAO_ESTOQUE = {
    MovimentacaoEstoque.ENTRADA,
    MovimentacaoEstoque.SAIDA,
    MovimentacaoEstoque.AJUSTE,
}


def filtrar_por_busca(queryset, termo):
    termo = (termo or "").strip()

    if not termo:
        return queryset

    return queryset.filter(
        Q(acolhimento__numero_bam__icontains=termo)
        | Q(acolhimento__paciente__nome_completo__icontains=termo)
        | Q(acolhimento__nome_paciente__icontains=termo)
        | Q(medico_responsavel__icontains=termo)
        | Q(crm_medico__icontains=termo)
        | Q(prescricao__icontains=termo)
        | Q(medicamentos_dispensados__icontains=termo)
    )


def farmacia_dashboard(request):
    busca = request.GET.get("q", "").strip()

    base = (
        ConsultaMedica.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .filter(solicita_medicacao=True)
    )

    pendentes_base = (
        base
        .filter(farmacia_liberada=False)
        .exclude(acolhimento__status__in=["FINALIZADO", "AUSENTE"])
        .order_by("data_consulta")
    )

    liberadas_base = (
        base
        .filter(farmacia_liberada=True)
        .order_by("-data_liberacao_farmacia")
    )

    medicacoes_pendentes = filtrar_por_busca(pendentes_base, busca)
    medicacoes_liberadas = filtrar_por_busca(liberadas_base, busca)

    total_pendentes = pendentes_base.count()
    total_liberadas = liberadas_base.count()
    total_administradas = liberadas_base.filter(medicacao_realizada=True).count()
    total_aguardando_enfermagem = (
        liberadas_base
        .filter(medicacao_realizada=False)
        .exclude(acolhimento__status__in=["FINALIZADO", "AUSENTE"])
        .count()
    )

    return render(
        request,
        "farmacia/dashboard.html",
        {
            "busca": busca,
            "medicacoes_pendentes": medicacoes_pendentes,
            "medicacoes_liberadas": medicacoes_liberadas,
            "total_pendentes": total_pendentes,
            "total_liberadas": total_liberadas,
            "total_administradas": total_administradas,
            "total_aguardando_enfermagem": total_aguardando_enfermagem,
        }
    )


def buscar_medicamento_estoque(request):
    termo = request.GET.get("q", "").strip()
    categoria = request.GET.get("categoria", "").strip()
    metodo_aplicacao = request.GET.get("metodo_aplicacao", "").strip()

    if len(termo) < 2 and not categoria and not metodo_aplicacao:
        return JsonResponse({
            "total": 0,
            "resultados": [],
        })

    medicamentos = MedicamentoEstoque.objects.filter(
        ativo=True,
        estoque_atual__gt=0
    )

    if termo:
        medicamentos = medicamentos.filter(
            Q(nome__icontains=termo)
            | Q(principio_ativo__icontains=termo)
            | Q(apresentacao__icontains=termo)
            | Q(concentracao__icontains=termo)
            | Q(lote_atual__icontains=termo)
            | Q(localizacao__icontains=termo)
            | Q(categoria__icontains=termo)
            | Q(metodo_aplicacao__icontains=termo)
        )

    if categoria:
        medicamentos = medicamentos.filter(categoria=categoria)

    if metodo_aplicacao:
        medicamentos = medicamentos.filter(metodo_aplicacao=metodo_aplicacao)

    total = medicamentos.count()

    medicamentos = medicamentos.order_by(
        "categoria",
        "nome",
        "concentracao",
        "apresentacao"
    )[:20]

    resultados = []

    for medicamento in medicamentos:
        resultados.append({
            "id": medicamento.id,
            "nome": medicamento.descricao_completa,
            "categoria": medicamento.get_categoria_display(),
            "metodo": medicamento.get_metodo_aplicacao_display(),
            "principio_ativo": medicamento.principio_ativo,
            "localizacao": medicamento.localizacao,
            "estoque": medicamento.estoque_atual,
            "unidade": medicamento.unidade_medida,
            "lote": medicamento.lote_atual,
            "validade": medicamento.validade.strftime("%d/%m/%Y") if medicamento.validade else "",
            "dias_validade": medicamento.texto_dias_validade,
        })

    return JsonResponse({
        "total": total,
        "resultados": resultados,
    })


def nome_paciente_consulta(consulta):
    if consulta.acolhimento.paciente:
        return consulta.acolhimento.paciente.nome_completo

    return consulta.acolhimento.nome_paciente


def baixar_itens_estoque(consulta, itens_estoque, form):
    itens_baixa = []

    for item in itens_estoque:
        try:
            medicamento = (
                MedicamentoEstoque.objects
                .select_for_update()
                .get(
                    id=item["medicamento_id"],
                    ativo=True
                )
            )
        except MedicamentoEstoque.DoesNotExist:
            form.add_error(
                "itens_estoque_json",
                "Um dos medicamentos selecionados nao esta mais disponivel no estoque."
            )
            continue

        quantidade = item["quantidade"]

        if medicamento.estoque_atual < quantidade:
            form.add_error(
                "itens_estoque_json",
                (
                    f"Estoque insuficiente para {medicamento.descricao_completa}. "
                    f"Disponivel: {medicamento.estoque_atual} {medicamento.unidade_medida}."
                )
            )
            continue

        itens_baixa.append((medicamento, quantidade))

    if form.errors:
        return False

    paciente = nome_paciente_consulta(consulta)
    destino = f"BAM {consulta.acolhimento.numero_bam} - {paciente}"[:180]

    for medicamento, quantidade in itens_baixa:
        saldo_anterior = medicamento.estoque_atual
        saldo_atual = saldo_anterior - quantidade

        MovimentacaoEstoque.objects.create(
            medicamento=medicamento,
            consulta=consulta,
            tipo=MovimentacaoEstoque.SAIDA,
            quantidade=quantidade,
            saldo_anterior=saldo_anterior,
            saldo_atual=saldo_atual,
            lote=consulta.lote_farmacia or medicamento.lote_atual or "",
            validade=consulta.validade_farmacia or medicamento.validade,
            origem_destino=destino,
            profissional_nome=consulta.profissional_farmacia_nome,
            profissional_registro=consulta.profissional_farmacia_registro or "",
            observacao=(
                "Saida por dispensacao da farmacia."
                + (
                    f" Observacao: {consulta.observacao_farmacia}"
                    if consulta.observacao_farmacia
                    else ""
                )
            ),
        )

        medicamento.estoque_atual = saldo_atual
        medicamento.save(update_fields=["estoque_atual", "atualizado_em"])

    return True


def liberar_medicacao(request, consulta_id):
    consulta = get_object_or_404(
        ConsultaMedica.objects.select_related(
            "acolhimento",
            "acolhimento__paciente"
        ),
        id=consulta_id,
        solicita_medicacao=True,
    )

    ja_liberada = consulta.farmacia_liberada

    if request.method == "POST":
        form = FarmaciaForm(
            request.POST,
            instance=consulta,
            exigir_itens_estoque=not ja_liberada
        )

        if form.is_valid():
            with transaction.atomic():
                consulta = form.save(commit=False)

                if not ja_liberada:
                    baixa_ok = baixar_itens_estoque(
                        consulta,
                        getattr(form, "itens_estoque", []),
                        form
                    )
                else:
                    baixa_ok = True

                if baixa_ok:
                    if not consulta.farmacia_liberada:
                        consulta.data_liberacao_farmacia = timezone.now()

                    consulta.farmacia_liberada = True
                    consulta.save()

                    acolhimento = consulta.acolhimento

                    if acolhimento.status not in ["FINALIZADO", "AUSENTE"]:
                        acolhimento.status = "PROCEDIMENTOS"
                        acolhimento.save(update_fields=["status"])

                    if ja_liberada:
                        messages.success(
                            request,
                            "Liberacao da farmacia atualizada com sucesso."
                        )
                    else:
                        messages.success(
                            request,
                            "Medicacao liberada pela farmacia com baixa automatica no estoque."
                        )

                    return redirect("farmacia_dashboard")
    else:
        form = FarmaciaForm(
            instance=consulta,
            exigir_itens_estoque=not ja_liberada
        )

    return render(
        request,
        "farmacia/liberar_medicacao.html",
        {
            "form": form,
            "consulta": consulta,
            "acolhimento": consulta.acolhimento,
            "ja_liberada": ja_liberada,
            "categorias": MedicamentoEstoque.CATEGORIA_CHOICES,
            "metodos_aplicacao": MedicamentoEstoque.METODO_APLICACAO_CHOICES,
        }
    )


def estoque_dashboard(request):
    busca = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    categoria = request.GET.get("categoria", "").strip()
    metodo_aplicacao = request.GET.get("metodo_aplicacao", "").strip()
    hoje = date.today()
    limite_vencimento = hoje + timedelta(days=30)

    medicamentos = MedicamentoEstoque.objects.all()

    if busca:
        medicamentos = medicamentos.filter(
            Q(nome__icontains=busca)
            | Q(principio_ativo__icontains=busca)
            | Q(apresentacao__icontains=busca)
            | Q(concentracao__icontains=busca)
            | Q(lote_atual__icontains=busca)
            | Q(localizacao__icontains=busca)
            | Q(categoria__icontains=busca)
            | Q(metodo_aplicacao__icontains=busca)
        )

    if categoria:
        medicamentos = medicamentos.filter(categoria=categoria)

    if metodo_aplicacao:
        medicamentos = medicamentos.filter(metodo_aplicacao=metodo_aplicacao)

    if status == "ativos":
        medicamentos = medicamentos.filter(ativo=True)
    elif status == "baixos":
        medicamentos = medicamentos.filter(
            ativo=True,
            estoque_atual__lte=F("estoque_minimo")
        )
    elif status == "zerados":
        medicamentos = medicamentos.filter(
            ativo=True,
            estoque_atual__lte=0
        )
    elif status == "inativos":
        medicamentos = medicamentos.filter(ativo=False)
    elif status == "vencidos":
        medicamentos = medicamentos.filter(
            ativo=True,
            validade__lt=hoje
        )
    elif status == "vencendo":
        medicamentos = medicamentos.filter(
            ativo=True,
            validade__gte=hoje,
            validade__lte=limite_vencimento
        )

    medicamentos = medicamentos.order_by(
        "categoria",
        "nome",
        "concentracao",
        "apresentacao"
    )

    paginator = Paginator(medicamentos, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    filtros_querystring = request.GET.copy()
    filtros_querystring.pop("page", None)

    ultimas_movimentacoes = (
        MovimentacaoEstoque.objects
        .select_related("medicamento")
        .order_by("-criado_em")[:20]
    )

    total_medicamentos = MedicamentoEstoque.objects.filter(ativo=True).count()
    total_estoque_baixo = MedicamentoEstoque.objects.filter(
        ativo=True,
        estoque_atual__lte=F("estoque_minimo")
    ).count()
    total_zerados = MedicamentoEstoque.objects.filter(
        ativo=True,
        estoque_atual__lte=0
    ).count()
    total_vencendo = MedicamentoEstoque.objects.filter(
        ativo=True,
        validade__gte=hoje,
        validade__lte=limite_vencimento
    ).count()
    total_vencidos = MedicamentoEstoque.objects.filter(
        ativo=True,
        validade__lt=hoje
    ).count()

    return render(
        request,
        "farmacia/estoque.html",
        {
            "busca": busca,
            "status": status,
            "categoria": categoria,
            "metodo_aplicacao": metodo_aplicacao,
            "categorias": MedicamentoEstoque.CATEGORIA_CHOICES,
            "metodos_aplicacao": MedicamentoEstoque.METODO_APLICACAO_CHOICES,
            "medicamentos": page_obj,
            "page_obj": page_obj,
            "total_filtrado": paginator.count,
            "filtros_querystring": filtros_querystring.urlencode(),
            "ultimas_movimentacoes": ultimas_movimentacoes,
            "total_medicamentos": total_medicamentos,
            "total_estoque_baixo": total_estoque_baixo,
            "total_zerados": total_zerados,
            "total_vencendo": total_vencendo,
            "total_vencidos": total_vencidos,
            "data_impressao_padrao": hoje.isoformat(),
            "mes_impressao_padrao": hoje.strftime("%Y-%m"),
        }
    )


def periodo_movimentacoes_impressao(request):
    hoje = date.today()
    tipo = (request.GET.get("tipo") or "dia").strip().lower()

    if tipo == "mes":
        mes_texto = (request.GET.get("mes") or hoje.strftime("%Y-%m")).strip()

        try:
            ano, mes = [int(parte) for parte in mes_texto.split("-", 1)]
            inicio_data = date(ano, mes, 1)
        except (TypeError, ValueError):
            inicio_data = date(hoje.year, hoje.month, 1)

        if inicio_data.month == 12:
            fim_data = date(inicio_data.year + 1, 1, 1)
        else:
            fim_data = date(inicio_data.year, inicio_data.month + 1, 1)

        return {
            "tipo": "mes",
            "titulo": "Movimentacoes por mes",
            "periodo_label": inicio_data.strftime("%m/%Y"),
            "inicio": datetime.combine(inicio_data, datetime.min.time()),
            "fim": datetime.combine(fim_data, datetime.min.time()),
        }

    data_texto = (request.GET.get("data") or hoje.isoformat()).strip()
    data = parse_date(data_texto) or hoje
    fim_data = data + timedelta(days=1)

    return {
        "tipo": "dia",
        "titulo": "Movimentacoes por dia",
        "periodo_label": data.strftime("%d/%m/%Y"),
        "inicio": datetime.combine(data, datetime.min.time()),
        "fim": datetime.combine(fim_data, datetime.min.time()),
    }


def resumo_movimentacoes(movimentacoes):
    resumo = {
        MovimentacaoEstoque.ENTRADA: {
            "rotulo": "Entradas",
            "classe": "entrada",
            "total": 0,
            "quantidade": 0,
        },
        MovimentacaoEstoque.SAIDA: {
            "rotulo": "Saidas",
            "classe": "saida",
            "total": 0,
            "quantidade": 0,
        },
        MovimentacaoEstoque.AJUSTE: {
            "rotulo": "Ajustes",
            "classe": "ajuste",
            "total": 0,
            "quantidade": 0,
        },
    }

    for movimentacao in movimentacoes:
        item = resumo.get(movimentacao.tipo)

        if not item:
            continue

        item["total"] += 1
        item["quantidade"] += movimentacao.quantidade

    return resumo.values()


def imprimir_movimentacoes_estoque(request):
    periodo = periodo_movimentacoes_impressao(request)
    movimentacoes = list(
        MovimentacaoEstoque.objects
        .select_related("medicamento")
        .filter(
            criado_em__gte=periodo["inicio"],
            criado_em__lt=periodo["fim"],
        )
        .order_by("criado_em", "medicamento__nome")
    )

    return render(
        request,
        "farmacia/imprimir_movimentacoes.html",
        {
            "periodo": periodo,
            "movimentacoes": movimentacoes,
            "resumo": resumo_movimentacoes(movimentacoes),
            "total_movimentacoes": len(movimentacoes),
            "gerado_em": datetime.now(),
        }
    )


def redirect_estoque_lote(request):
    destino = request.POST.get("next") or reverse("farmacia_estoque")

    return redirect(destino)


def quantidade_lote_valida(tipo, medicamento_id, request):
    valor = request.POST.get(f"quantidade_{medicamento_id}", "").strip()

    if not valor or "." in valor or "," in valor:
        raise ValueError("Informe quantidades inteiras para todos os itens selecionados.")

    quantidade = int(valor)

    if tipo == MovimentacaoEstoque.AJUSTE:
        if quantidade < 0:
            raise ValueError("O novo saldo nao pode ser negativo.")
    elif quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")

    return quantidade


def dados_lote_validade_por_item(ids, request):
    dados = {}
    lote_padrao = (request.POST.get("lote") or "").strip()
    validade_padrao_texto = (request.POST.get("validade") or "").strip()

    for medicamento_id in ids:
        lote = (request.POST.get(f"lote_{medicamento_id}") or lote_padrao).strip()
        validade_texto = (
            request.POST.get(f"validade_{medicamento_id}")
            or validade_padrao_texto
        ).strip()
        validade = None

        if validade_texto:
            validade = parse_date(validade_texto)

            if validade is None:
                raise ValueError(
                    "Informe uma data de validade valida para todos os itens selecionados."
                )

        dados[medicamento_id] = {
            "lote": lote,
            "validade": validade,
        }

    return dados


def saldo_movimentado(tipo, saldo_anterior, quantidade):
    if tipo == MovimentacaoEstoque.ENTRADA:
        return saldo_anterior + quantidade

    if tipo == MovimentacaoEstoque.SAIDA:
        return saldo_anterior - quantidade

    return quantidade


def descricao_tipo_lote(tipo):
    if tipo == MovimentacaoEstoque.ENTRADA:
        return "entrada"

    if tipo == MovimentacaoEstoque.SAIDA:
        return "saida"

    return "ajuste"


def campos_atualizacao_estoque(medicamento, tipo, lote=None, validade=None):
    update_fields = ["estoque_atual", "atualizado_em"]

    if tipo in {MovimentacaoEstoque.ENTRADA, MovimentacaoEstoque.AJUSTE}:
        if lote:
            medicamento.lote_atual = lote
            update_fields.append("lote_atual")

        if validade:
            medicamento.validade = validade
            update_fields.append("validade")

    return update_fields


def movimentar_estoque_lote(request):
    if request.method != "POST":
        return redirect("farmacia_estoque")

    tipo = (request.POST.get("tipo_movimentacao") or "").upper()
    ids_texto = request.POST.getlist("medicamentos")
    profissional_nome = (request.POST.get("profissional_nome") or "").strip()
    profissional_registro = (request.POST.get("profissional_registro") or "").strip()
    origem_destino = (request.POST.get("origem_destino") or "").strip()
    observacao = (request.POST.get("observacao") or "").strip()

    if tipo not in TIPOS_MOVIMENTACAO_ESTOQUE:
        messages.error(request, "Tipo de movimentacao em lote invalido.")
        return redirect_estoque_lote(request)

    if not ids_texto:
        messages.warning(request, "Marque pelo menos um medicamento para movimentar.")
        return redirect_estoque_lote(request)

    if not profissional_nome:
        messages.error(request, "Informe o nome do profissional responsavel.")
        return redirect_estoque_lote(request)

    try:
        ids = [int(medicamento_id) for medicamento_id in ids_texto]
    except ValueError:
        messages.error(request, "Lista de medicamentos selecionados invalida.")
        return redirect_estoque_lote(request)

    if len(set(ids)) != len(ids):
        messages.error(request, "Ha medicamento repetido na selecao.")
        return redirect_estoque_lote(request)

    try:
        quantidades = {
            medicamento_id: quantidade_lote_valida(tipo, medicamento_id, request)
            for medicamento_id in ids
        }
    except ValueError as erro:
        messages.error(request, str(erro))
        return redirect_estoque_lote(request)

    try:
        dados_por_item = dados_lote_validade_por_item(ids, request)
    except ValueError as erro:
        messages.error(request, str(erro))
        return redirect_estoque_lote(request)

    with transaction.atomic():
        medicamentos = list(
            MedicamentoEstoque.objects
            .select_for_update()
            .filter(id__in=ids)
        )

        medicamentos_por_id = {
            medicamento.id: medicamento
            for medicamento in medicamentos
        }

        if len(medicamentos_por_id) != len(ids):
            messages.error(request, "Um dos medicamentos selecionados nao foi encontrado.")
            return redirect_estoque_lote(request)

        for medicamento_id in ids:
            medicamento = medicamentos_por_id[medicamento_id]
            quantidade = quantidades[medicamento_id]

            if tipo == MovimentacaoEstoque.SAIDA and quantidade > medicamento.estoque_atual:
                messages.error(
                    request,
                    (
                        f"Estoque insuficiente para {medicamento.descricao_completa}. "
                        f"Disponivel: {medicamento.estoque_atual} {medicamento.unidade_medida}."
                    )
                )
                return redirect_estoque_lote(request)

        for medicamento_id in ids:
            medicamento = medicamentos_por_id[medicamento_id]
            quantidade = quantidades[medicamento_id]
            saldo_anterior = medicamento.estoque_atual
            saldo_atual = saldo_movimentado(tipo, saldo_anterior, quantidade)
            dados_item = dados_por_item[medicamento_id]

            MovimentacaoEstoque.objects.create(
                medicamento=medicamento,
                tipo=tipo,
                quantidade=quantidade,
                saldo_anterior=saldo_anterior,
                saldo_atual=saldo_atual,
                lote=dados_item["lote"],
                validade=dados_item["validade"],
                origem_destino=origem_destino,
                profissional_nome=profissional_nome,
                profissional_registro=profissional_registro,
                observacao=observacao,
            )

            medicamento.estoque_atual = saldo_atual
            medicamento.save(
                update_fields=campos_atualizacao_estoque(
                    medicamento,
                    tipo,
                    lote=dados_item["lote"],
                    validade=dados_item["validade"]
                )
            )

    messages.success(
        request,
        (
            f"{len(ids)} medicamento(s) movimentado(s) em lote "
            f"com {descricao_tipo_lote(tipo)} no estoque."
        )
    )

    return redirect_estoque_lote(request)


def cadastrar_medicamento(request, medicamento_id=None):
    medicamento = None

    if medicamento_id:
        medicamento = get_object_or_404(MedicamentoEstoque, id=medicamento_id)

    if request.method == "POST":
        form = MedicamentoEstoqueForm(request.POST, instance=medicamento)

        if form.is_valid():
            form.save()

            if medicamento:
                messages.success(request, "Medicamento atualizado com sucesso.")
            else:
                messages.success(request, "Medicamento cadastrado com sucesso.")

            return redirect("farmacia_estoque")
    else:
        form = MedicamentoEstoqueForm(instance=medicamento)

    return render(
        request,
        "farmacia/medicamento_form.html",
        {
            "form": form,
            "medicamento": medicamento,
        }
    )


def movimentar_estoque(request, medicamento_id, tipo):
    medicamento = get_object_or_404(MedicamentoEstoque, id=medicamento_id)
    tipo = (tipo or "").upper()

    if tipo not in [
        MovimentacaoEstoque.ENTRADA,
        MovimentacaoEstoque.SAIDA,
        MovimentacaoEstoque.AJUSTE,
    ]:
        messages.error(request, "Tipo de movimentacao invalido.")
        return redirect("farmacia_estoque")

    if request.method == "POST":
        form = MovimentacaoEstoqueForm(
            request.POST,
            tipo_movimento=tipo
        )

        if form.is_valid():
            quantidade = form.cleaned_data["quantidade"]

            with transaction.atomic():
                medicamento_bloqueado = (
                    MedicamentoEstoque.objects
                    .select_for_update()
                    .get(id=medicamento.id)
                )

                saldo_anterior = medicamento_bloqueado.estoque_atual

                if tipo == MovimentacaoEstoque.ENTRADA:
                    saldo_atual = saldo_anterior + quantidade
                elif tipo == MovimentacaoEstoque.SAIDA:
                    if quantidade > saldo_anterior:
                        form.add_error(
                            "quantidade",
                            "Quantidade maior que o saldo disponivel."
                        )
                        saldo_atual = None
                    else:
                        saldo_atual = saldo_anterior - quantidade
                else:
                    saldo_atual = quantidade

                if saldo_atual is not None:
                    movimentacao = form.save(commit=False)
                    movimentacao.medicamento = medicamento_bloqueado
                    movimentacao.tipo = tipo
                    movimentacao.quantidade = quantidade
                    movimentacao.saldo_anterior = saldo_anterior
                    movimentacao.saldo_atual = saldo_atual
                    movimentacao.save()

                    medicamento_bloqueado.estoque_atual = saldo_atual
                    medicamento_bloqueado.save(
                        update_fields=campos_atualizacao_estoque(
                            medicamento_bloqueado,
                            tipo,
                            lote=movimentacao.lote,
                            validade=movimentacao.validade
                        )
                    )

                    messages.success(request, "Movimentacao registrada com sucesso.")
                    return redirect("farmacia_estoque")
    else:
        form = MovimentacaoEstoqueForm(tipo_movimento=tipo)

    return render(
        request,
        "farmacia/movimentar_estoque.html",
        {
            "form": form,
            "medicamento": medicamento,
            "tipo": tipo,
        }
    )
