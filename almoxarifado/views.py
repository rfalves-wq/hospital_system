from datetime import date, timedelta

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.utils import nome_profissional_request, registro_profissional_request

from .forms import MaterialAlmoxarifadoForm, MovimentacaoAlmoxarifadoForm
from .models import MaterialAlmoxarifado, MovimentacaoAlmoxarifado


TIPOS_MOVIMENTACAO = {
    MovimentacaoAlmoxarifado.ENTRADA,
    MovimentacaoAlmoxarifado.SAIDA,
    MovimentacaoAlmoxarifado.AJUSTE,
}


def filtrar_materiais(materiais, busca):
    busca = (busca or "").strip()

    if not busca:
        return materiais

    return materiais.filter(
        Q(nome__icontains=busca)
        | Q(codigo__icontains=busca)
        | Q(descricao__icontains=busca)
        | Q(marca__icontains=busca)
        | Q(fornecedor__icontains=busca)
        | Q(localizacao__icontains=busca)
        | Q(lote_atual__icontains=busca)
    )


def dashboard(request):
    busca = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    categoria = request.GET.get("categoria", "").strip()
    hoje = date.today()
    limite_vencimento = hoje + timedelta(days=30)

    materiais = filtrar_materiais(MaterialAlmoxarifado.objects.all(), busca)

    if categoria:
        materiais = materiais.filter(categoria=categoria)

    if status == "ativos":
        materiais = materiais.filter(ativo=True)
    elif status == "baixos":
        materiais = materiais.filter(ativo=True, estoque_atual__lte=F("estoque_minimo"))
    elif status == "zerados":
        materiais = materiais.filter(ativo=True, estoque_atual__lte=0)
    elif status == "inativos":
        materiais = materiais.filter(ativo=False)
    elif status == "vencidos":
        materiais = materiais.filter(ativo=True, validade__lt=hoje)
    elif status == "vencendo":
        materiais = materiais.filter(
            ativo=True,
            validade__gte=hoje,
            validade__lte=limite_vencimento,
        )

    materiais = materiais.order_by("categoria", "nome", "marca")
    paginator = Paginator(materiais, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    filtros_querystring = request.GET.copy()
    filtros_querystring.pop("page", None)

    total_ativos = MaterialAlmoxarifado.objects.filter(ativo=True).count()
    total_baixos = MaterialAlmoxarifado.objects.filter(
        ativo=True,
        estoque_atual__lte=F("estoque_minimo"),
    ).count()
    total_zerados = MaterialAlmoxarifado.objects.filter(
        ativo=True,
        estoque_atual__lte=0,
    ).count()
    total_vencendo = MaterialAlmoxarifado.objects.filter(
        ativo=True,
        validade__gte=hoje,
        validade__lte=limite_vencimento,
    ).count()
    total_vencidos = MaterialAlmoxarifado.objects.filter(
        ativo=True,
        validade__lt=hoje,
    ).count()

    ultimas_movimentacoes = (
        MovimentacaoAlmoxarifado.objects
        .select_related("material")
        .order_by("-criado_em")[:18]
    )

    return render(
        request,
        "almoxarifado/dashboard.html",
        {
            "busca": busca,
            "status": status,
            "categoria": categoria,
            "categorias": MaterialAlmoxarifado.CATEGORIA_CHOICES,
            "materiais": page_obj,
            "page_obj": page_obj,
            "total_filtrado": paginator.count,
            "filtros_querystring": filtros_querystring.urlencode(),
            "total_ativos": total_ativos,
            "total_baixos": total_baixos,
            "total_zerados": total_zerados,
            "total_vencendo": total_vencendo,
            "total_vencidos": total_vencidos,
            "ultimas_movimentacoes": ultimas_movimentacoes,
        },
    )


def cadastrar_material(request, material_id=None):
    material = None

    if material_id:
        material = get_object_or_404(MaterialAlmoxarifado, id=material_id)

    if request.method == "POST":
        form = MaterialAlmoxarifadoForm(request.POST, instance=material)

        if form.is_valid():
            form.save()

            if material:
                messages.success(request, "Material atualizado com sucesso.")
            else:
                messages.success(request, "Material cadastrado com sucesso.")

            return redirect("almoxarifado_dashboard")
    else:
        form = MaterialAlmoxarifadoForm(instance=material)

    return render(
        request,
        "almoxarifado/material_form.html",
        {
            "form": form,
            "material": material,
        },
    )


def saldo_movimentado(tipo, saldo_anterior, quantidade):
    if tipo == MovimentacaoAlmoxarifado.ENTRADA:
        return saldo_anterior + quantidade

    if tipo == MovimentacaoAlmoxarifado.SAIDA:
        return saldo_anterior - quantidade

    return quantidade


def campos_atualizacao_material(material, tipo, lote=None, validade=None):
    campos = ["estoque_atual", "atualizado_em"]

    if tipo in {MovimentacaoAlmoxarifado.ENTRADA, MovimentacaoAlmoxarifado.AJUSTE}:
        if lote:
            material.lote_atual = lote
            campos.append("lote_atual")

        if validade:
            material.validade = validade
            campos.append("validade")

    return campos


def movimentar_material(request, material_id, tipo):
    material = get_object_or_404(MaterialAlmoxarifado, id=material_id)
    tipo = (tipo or "").upper()

    if tipo not in TIPOS_MOVIMENTACAO:
        messages.error(request, "Tipo de movimentacao invalido.")
        return redirect("almoxarifado_dashboard")

    if request.method == "POST":
        form = MovimentacaoAlmoxarifadoForm(
            request.POST,
            tipo_movimento=tipo,
        )

        if form.is_valid():
            quantidade = form.cleaned_data["quantidade"]

            with transaction.atomic():
                material_bloqueado = (
                    MaterialAlmoxarifado.objects
                    .select_for_update()
                    .get(id=material.id)
                )
                saldo_anterior = material_bloqueado.estoque_atual

                if tipo == MovimentacaoAlmoxarifado.SAIDA and quantidade > saldo_anterior:
                    form.add_error("quantidade", "Quantidade maior que o saldo disponivel.")
                    saldo_atual = None
                else:
                    saldo_atual = saldo_movimentado(tipo, saldo_anterior, quantidade)

                if saldo_atual is not None:
                    movimentacao = form.save(commit=False)
                    movimentacao.material = material_bloqueado
                    movimentacao.tipo = tipo
                    movimentacao.quantidade = quantidade
                    movimentacao.saldo_anterior = saldo_anterior
                    movimentacao.saldo_atual = saldo_atual
                    movimentacao.save()

                    material_bloqueado.estoque_atual = saldo_atual
                    material_bloqueado.save(
                        update_fields=campos_atualizacao_material(
                            material_bloqueado,
                            tipo,
                            lote=movimentacao.lote,
                            validade=movimentacao.validade,
                        )
                    )

                    messages.success(request, "Movimentacao registrada com sucesso.")
                    return redirect("almoxarifado_dashboard")
    else:
        form = MovimentacaoAlmoxarifadoForm(
            tipo_movimento=tipo,
            initial={
                "profissional_nome": nome_profissional_request(request),
                "profissional_registro": registro_profissional_request(request),
            },
        )

    return render(
        request,
        "almoxarifado/movimentar.html",
        {
            "form": form,
            "material": material,
            "tipo": tipo,
        },
    )
