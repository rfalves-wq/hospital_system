from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from acolhimento.models import Acolhimento
from farmacia.models import MedicamentoEstoque

from .forms import ConsultaMedicaForm
from .models import ConsultaMedica, CID


def medico_dashboard(request):

    acolhimentos = (
        Acolhimento.objects
        .select_related("paciente", "classificacao")
        .filter(status__in=["CONSULTA", "RETORNO_MEDICO"])
        .order_by("data_acolhimento")
    )

    nome_medico = ""

    if request.user.is_authenticated:
        nome_medico = (
            request.user.get_full_name()
            or request.user.username
        )

    minhas_consultas = (
        ConsultaMedica.objects
        .select_related(
            "acolhimento",
            "acolhimento__paciente",
            "acolhimento__classificacao"
        )
        .filter(medico_responsavel=nome_medico)
        .order_by("-data_consulta")
    )

    return render(
        request,
        "medico/dashboard.html",
        {
            "acolhimentos": acolhimentos,
            "total_consulta": acolhimentos.count(),
            "minhas_consultas": minhas_consultas,
            "total_minhas_consultas": minhas_consultas.count(),
        }
    )


def buscar_cid(request):

    termo = request.GET.get("q", "").strip()

    if len(termo) < 2:
        return JsonResponse([], safe=False)

    cids = (
        CID.objects
        .filter(
            Q(codigo__icontains=termo)
            | Q(descricao__icontains=termo)
        )
        .order_by("codigo")[:20]
    )

    dados = []

    for cid in cids:
        dados.append({
            "codigo": cid.codigo,
            "descricao": cid.descricao,
            "tipo": cid.tipo,
        })

    return JsonResponse(dados, safe=False)


def buscar_medicamento_farmacia(request):

    termo = request.GET.get("q", "").strip()
    categoria = request.GET.get("categoria", "").strip()
    metodo = request.GET.get("metodo", "").strip()

    if len(termo) < 2 and not categoria and not metodo:
        return JsonResponse(
            {
                "total": 0,
                "resultados": [],
            }
        )

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

    if metodo:
        medicamentos = medicamentos.filter(metodo_aplicacao=metodo)

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
            "texto": f"{medicamento.descricao_completa} - {medicamento.get_metodo_aplicacao_display()}",
            "categoria": medicamento.get_categoria_display(),
            "metodo": medicamento.get_metodo_aplicacao_display(),
            "principio_ativo": medicamento.principio_ativo,
            "localizacao": medicamento.localizacao,
            "estoque": str(medicamento.estoque_atual),
            "unidade": medicamento.unidade_medida,
        })

    return JsonResponse(
        {
            "total": total,
            "resultados": resultados,
        }
    )


def atender_paciente(request, acolhimento_id):

    acolhimento = get_object_or_404(
        Acolhimento,
        id=acolhimento_id
    )

    consulta = ConsultaMedica.objects.filter(
        acolhimento=acolhimento
    ).first()

    try:
        classificacao = acolhimento.classificacao
    except ObjectDoesNotExist:
        classificacao = None

    if request.method == "POST":

        form = ConsultaMedicaForm(
            request.POST,
            instance=consulta
        )

        if form.is_valid():

            consulta_medica = form.save(commit=False)
            consulta_medica.acolhimento = acolhimento
            consulta_medica.save()

            tem_procedimento = (
                consulta_medica.solicita_medicacao
                or consulta_medica.solicita_exames_laboratoriais
                or consulta_medica.solicita_exames_imagem
            )

            if tem_procedimento:
                acolhimento.status = "PROCEDIMENTOS"

            elif consulta_medica.conduta == "ALTA":
                acolhimento.status = "FINALIZADO"

            elif consulta_medica.conduta == "OBSERVACAO":
                acolhimento.status = "OBSERVACAO"

            elif consulta_medica.conduta == "INTERNACAO":
                acolhimento.status = "INTERNACAO"

            else:
                acolhimento.status = "RETORNO_MEDICO"

            acolhimento.save()

            messages.success(
                request,
                "Consulta médica salva com sucesso. Paciente encaminhado conforme a conduta."
            )

            return redirect("medico_dashboard")

    else:

        inicial = {}

        if classificacao:
            inicial["queixa_principal"] = classificacao.queixa_principal

        if request.user.is_authenticated:
            inicial["medico_responsavel"] = (
                request.user.get_full_name()
                or request.user.username
            )

        form = ConsultaMedicaForm(
            instance=consulta,
            initial=inicial
        )

    total_medicamentos_farmacia = MedicamentoEstoque.objects.filter(
        ativo=True,
        estoque_atual__gt=0
    ).count()

    return render(
        request,
        "medico/atender.html",
        {
            "form": form,
            "acolhimento": acolhimento,
            "classificacao": classificacao,
            "consulta": consulta,
            "categorias_farmacia": MedicamentoEstoque.CATEGORIA_CHOICES,
            "metodos_aplicacao_farmacia": MedicamentoEstoque.METODO_APLICACAO_CHOICES,
            "total_medicamentos_farmacia": total_medicamentos_farmacia,
        }
    )


def retornar_para_medico(request, acolhimento_id):

    acolhimento = get_object_or_404(
        Acolhimento,
        id=acolhimento_id
    )

    acolhimento.status = "RETORNO_MEDICO"
    acolhimento.save()

    messages.success(
        request,
        "Paciente encaminhado para retorno médico."
    )

    return redirect("medico_dashboard")
