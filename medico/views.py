from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from acolhimento.models import Acolhimento
from acolhimento.utils import passagens_do_paciente_no_dia
from farmacia.models import MedicamentoEstoque

from .forms import ConsultaMedicaForm
from .models import ConsultaMedica, CID


def medico_dashboard(request):
    dados_impressao = buscar_dados_impressao_medico(request)

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
            "dados_impressao_medico": dados_impressao,
        }
    )


def buscar_dados_impressao_medico(request):
    consulta_id = request.session.pop("medico_impressao_consulta_id", None)

    if not consulta_id:
        return None

    try:
        consulta = (
            ConsultaMedica.objects
            .select_related(
                "acolhimento",
                "acolhimento__paciente",
                "acolhimento__classificacao"
            )
            .get(id=consulta_id)
        )
    except ConsultaMedica.DoesNotExist:
        return None

    return dados_consulta_para_impressao(consulta)


def formatar_data(valor):
    return valor.strftime("%d/%m/%Y") if valor else ""


def formatar_data_hora(valor):
    if not valor:
        return ""

    if timezone.is_aware(valor):
        valor = timezone.localtime(valor)

    return valor.strftime("%d/%m/%Y %H:%M")


def formatar_hora(valor):
    return valor.strftime("%H:%M") if valor else ""


def formatar_decimal(valor):
    if valor is None:
        return ""

    return str(valor).replace(".", ",")


def nome_paciente_acolhimento(acolhimento):
    if acolhimento.paciente:
        return acolhimento.paciente.nome_completo

    return acolhimento.nome_paciente


def dados_base_para_impressao(acolhimento, classificacao=None):
    paciente = acolhimento.paciente

    if classificacao is None:
        try:
            classificacao = acolhimento.classificacao
        except ObjectDoesNotExist:
            classificacao = None

    _, _, passagens_hospital_dia = passagens_do_paciente_no_dia(acolhimento)

    return {
        "bam": acolhimento.numero_bam or "",
        "paciente": nome_paciente_acolhimento(acolhimento),
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
        "passagens": f"{passagens_hospital_dia.count()} hoje",
        "classificacao": (
            classificacao.get_cor_display()
            if classificacao
            else ""
        ),
        "queixaClassificacao": (
            classificacao.queixa_principal
            if classificacao and classificacao.queixa_principal
            else ""
        ),
        "dataClassificacao": (
            formatar_data_hora(classificacao.data_classificacao)
            if classificacao
            else ""
        ),
    }


def dados_consulta_para_impressao(consulta):
    dados = dados_base_para_impressao(consulta.acolhimento)

    dados.update({
        "medicoResponsavel": consulta.medico_responsavel or "",
        "crmMedico": consulta.crm_medico or "",
        "dataConsulta": formatar_data_hora(consulta.data_consulta),
        "cid": consulta.cid or "",
        "queixaPrincipal": consulta.queixa_principal or "",
        "historiaDoencaAtual": consulta.historia_doenca_atual or "",
        "exameFisico": consulta.exame_fisico or "",
        "hipoteseDiagnostica": consulta.hipotese_diagnostica or "",
        "conduta": consulta.get_conduta_display(),
        "condutaCodigo": consulta.conduta or "",
        "solicitaMedicacao": consulta.solicita_medicacao,
        "solicitaLaboratorio": consulta.solicita_exames_laboratoriais,
        "solicitaImagem": consulta.solicita_exames_imagem,
        "examesLaboratoriais": consulta.exames_laboratoriais or "",
        "examesImagem": consulta.exames_imagem or "",
        "indicacaoRaiox": consulta.indicacao_raiox or "",
        "indicacaoTomografia": consulta.indicacao_tomografia or "",
        "indicacaoOutrosImagem": consulta.indicacao_outros_imagem or "",
        "prescricao": consulta.prescricao or "",
        "orientacoes": consulta.orientacoes or "",
        "resultadoLaboratorio": consulta.resultado_exames_laboratoriais or "",
        "dataResultadoLaboratorio": formatar_data_hora(consulta.data_resultado_laboratorio),
        "resultadoImagem": consulta.resultado_exames_imagem or "",
        "dataResultadoImagem": formatar_data_hora(consulta.data_resultado_imagem),
        "resultadoRaiox": consulta.resultado_raiox or "",
        "dataResultadoRaiox": formatar_data_hora(consulta.data_resultado_raiox),
        "resultadoTomografia": consulta.resultado_tomografia or "",
        "dataResultadoTomografia": formatar_data_hora(consulta.data_resultado_tomografia),
        "resultadoMamografia": consulta.resultado_mamografia or "",
        "dataResultadoMamografia": formatar_data_hora(consulta.data_resultado_mamografia),
        "resultadoDensitometria": consulta.resultado_densitometria or "",
        "dataResultadoDensitometria": formatar_data_hora(consulta.data_resultado_densitometria),
        "medicamentosDispensados": consulta.medicamentos_dispensados or "",
        "medicacaoAdministrada": consulta.medicacao_administrada or "",
        "observacoesMedicacao": consulta.observacoes_medicacao or "",
        "farmaciaLiberada": consulta.farmacia_liberada,
        "imprimirTudo": consulta.conduta in ["ALTA", "INTERNACAO"],
    })

    return dados


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

            if consulta_medica.conduta == "ALTA":
                acolhimento.status = "FINALIZADO"

            elif consulta_medica.conduta == "INTERNACAO":
                acolhimento.status = "INTERNACAO"

            elif tem_procedimento:
                acolhimento.status = "PROCEDIMENTOS"

            elif consulta_medica.conduta == "OBSERVACAO":
                acolhimento.status = "OBSERVACAO"

            else:
                acolhimento.status = "RETORNO_MEDICO"

            acolhimento.save()

            if consulta_medica.conduta in ["ALTA", "INTERNACAO"]:
                request.session["medico_impressao_consulta_id"] = consulta_medica.id

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

    periodo_inicio, periodo_fim, passagens_hospital_dia = passagens_do_paciente_no_dia(acolhimento)

    total_passagens_hospital_dia = passagens_hospital_dia.count()
    tem_passagem_anterior_hoje = (
        passagens_hospital_dia
        .exclude(id=acolhimento.id)
        .exists()
    )

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
            "periodo_passagens_inicio": periodo_inicio,
            "periodo_passagens_fim": periodo_fim,
            "passagens_hospital_dia": passagens_hospital_dia,
            "total_passagens_hospital_dia": total_passagens_hospital_dia,
            "tem_passagem_anterior_hoje": tem_passagem_anterior_hoje,
            "dados_base_impressao_medico": dados_base_para_impressao(
                acolhimento,
                classificacao
            ),
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
