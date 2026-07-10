from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from medico.models import ConsultaMedica

from .forms import FarmaciaForm, MedicamentoEstoqueForm, MovimentacaoEstoqueForm
from .models import MedicamentoEstoque, MovimentacaoEstoque


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
        .exclude(acolhimento__status="FINALIZADO")
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
        .exclude(acolhimento__status="FINALIZADO")
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
            "estoque": str(medicamento.estoque_atual),
            "unidade": medicamento.unidade_medida,
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
            lote=consulta.lote_farmacia or "",
            validade=consulta.validade_farmacia,
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

                    if acolhimento.status != "FINALIZADO":
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

    medicamentos = MedicamentoEstoque.objects.all()

    if busca:
        medicamentos = medicamentos.filter(
            Q(nome__icontains=busca)
            | Q(principio_ativo__icontains=busca)
            | Q(apresentacao__icontains=busca)
            | Q(concentracao__icontains=busca)
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
        }
    )


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
                    medicamento_bloqueado.save(update_fields=["estoque_atual", "atualizado_em"])

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
