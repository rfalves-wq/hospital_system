from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from acolhimento.models import Acolhimento
from acolhimento.tempos import anexar_entrada_setor
from acolhimento.utils import passagens_do_paciente_no_dia, periodo_do_dia
from accounts.utils import nome_profissional_request, registro_profissional_request
from farmacia.models import MedicamentoEstoque
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

from .forms import ConsultaMedicaForm, ReavaliacaoMedicaForm
from .models import (
    ConsultaMedica,
    CID,
    ReavaliacaoMedica,
    TransferenciaConsultaMedica,
)


def nome_usuario(request):
    return nome_profissional_request(request)


STATUS_TRAVA_ATENDIMENTO_MEDICO = {"CONSULTA", "RETORNO_MEDICO"}
STATUS_NAO_EDITAVEL_MEDICO = {"FINALIZADO", "AUSENTE"}


def nomes_profissionais_iguais(nome_a, nome_b):
    return (nome_a or "").strip().casefold() == (nome_b or "").strip().casefold()


def atendimento_medico_bloqueado_por_outro(acolhimento, medico_atual):
    medico_em_atendimento = (acolhimento.medico_atendimento_nome or "").strip()

    return bool(
        acolhimento.status in STATUS_TRAVA_ATENDIMENTO_MEDICO
        and medico_em_atendimento
        and not nomes_profissionais_iguais(medico_em_atendimento, medico_atual)
    )


def consulta_medica_de_outro_profissional(consulta, medico_atual):
    if not consulta or not (consulta.medico_responsavel or "").strip():
        return False

    return not nomes_profissionais_iguais(
        consulta.medico_responsavel,
        medico_atual,
    )


def pode_editar_atendimento_medico(acolhimento, consulta, medico_atual):
    if not (medico_atual or "").strip():
        return False

    if acolhimento.status in STATUS_NAO_EDITAVEL_MEDICO:
        return False

    if atendimento_medico_bloqueado_por_outro(acolhimento, medico_atual):
        return False

    if consulta_medica_de_outro_profissional(consulta, medico_atual):
        return False

    return True


def dados_bloqueio_atendimento_medico(acolhimento, consulta, medico_atual):
    if atendimento_medico_bloqueado_por_outro(acolhimento, medico_atual):
        return {
            "titulo": "Paciente em atendimento por outro medico",
            "nome": acolhimento.medico_atendimento_nome,
            "registro": acolhimento.medico_atendimento_crm,
            "consultorio": acolhimento.medico_atendimento_consultorio,
            "inicio": acolhimento.medico_atendimento_inicio,
        }

    if consulta_medica_de_outro_profissional(consulta, medico_atual):
        return {
            "titulo": "Paciente sob responsabilidade de outro medico",
            "nome": consulta.medico_responsavel,
            "registro": consulta.crm_medico,
            "consultorio": "",
            "inicio": consulta.data_consulta,
        }

    return None


def bloquear_campos_formulario(form):
    for field in form.fields.values():
        field.disabled = True
        field.widget.attrs["disabled"] = "disabled"
        field.widget.attrs["aria-disabled"] = "true"


def marcar_atendimento_medico_em_andamento(
    acolhimento,
    medico_atual,
    crm_medico_atual,
    consultorio_atual,
    reiniciar=False,
):
    if not medico_atual or acolhimento.status not in STATUS_TRAVA_ATENDIMENTO_MEDICO:
        return False

    agora = timezone.now()
    campos = []

    if not nomes_profissionais_iguais(acolhimento.medico_atendimento_nome, medico_atual):
        acolhimento.medico_atendimento_nome = medico_atual
        campos.append("medico_atendimento_nome")

    crm_medico_atual = crm_medico_atual or ""
    if (acolhimento.medico_atendimento_crm or "") != crm_medico_atual:
        acolhimento.medico_atendimento_crm = crm_medico_atual
        campos.append("medico_atendimento_crm")

    consultorio_atual = consultorio_atual or ""
    if (acolhimento.medico_atendimento_consultorio or "") != consultorio_atual:
        acolhimento.medico_atendimento_consultorio = consultorio_atual
        campos.append("medico_atendimento_consultorio")

    if reiniciar or not acolhimento.medico_atendimento_inicio:
        acolhimento.medico_atendimento_inicio = agora
        campos.append("medico_atendimento_inicio")

    if campos:
        acolhimento.save(update_fields=campos)

    return bool(campos)


def limpar_atendimento_medico_em_andamento(acolhimento):
    campos = []

    if acolhimento.medico_atendimento_nome:
        acolhimento.medico_atendimento_nome = ""
        campos.append("medico_atendimento_nome")

    if acolhimento.medico_atendimento_crm:
        acolhimento.medico_atendimento_crm = ""
        campos.append("medico_atendimento_crm")

    if acolhimento.medico_atendimento_consultorio:
        acolhimento.medico_atendimento_consultorio = ""
        campos.append("medico_atendimento_consultorio")

    if acolhimento.medico_atendimento_inicio:
        acolhimento.medico_atendimento_inicio = None
        campos.append("medico_atendimento_inicio")

    if campos:
        acolhimento.save(update_fields=campos)

    return bool(campos)


def anexar_trava_medica_acolhimentos(acolhimentos, medico_atual):
    for acolhimento in acolhimentos:
        try:
            consulta = acolhimento.consulta_medica
        except ObjectDoesNotExist:
            consulta = None

        acolhimento.medico_bloqueado_por_outro = atendimento_medico_bloqueado_por_outro(
            acolhimento,
            medico_atual,
        )
        acolhimento.medico_pode_editar = pode_editar_atendimento_medico(
            acolhimento,
            consulta,
            medico_atual,
        )
        acolhimento.medico_bloqueio = dados_bloqueio_atendimento_medico(
            acolhimento,
            consulta,
            medico_atual,
        )


def anexar_trava_medica_consultas(consultas, medico_atual):
    for consulta in consultas:
        acolhimento = consulta.acolhimento
        consulta.medico_bloqueado_por_outro = atendimento_medico_bloqueado_por_outro(
            acolhimento,
            medico_atual,
        )
        consulta.medico_pode_editar = pode_editar_atendimento_medico(
            acolhimento,
            consulta,
            medico_atual,
        )
        consulta.medico_bloqueio = dados_bloqueio_atendimento_medico(
            acolhimento,
            consulta,
            medico_atual,
        )


def chave_consultorio_medico(request):
    if request.user.is_authenticated:
        return f"medico_consultorio_atual_{request.user.pk}"

    return "medico_consultorio_atual"


def normalizar_consultorio_medico(consultorio):
    consultorio = (consultorio or "").strip()
    consultorio = " ".join(consultorio.split())

    if consultorio.isdigit():
        consultorio = f"Consultorio {consultorio}"

    return consultorio[:80]


def consultorio_medico_atual(request):
    return request.session.get(chave_consultorio_medico(request), "")


def consultorio_medico_informado(request):
    return normalizar_consultorio_medico(request.POST.get("consultorio"))


def ultimo_consultorio_chamado(acolhimento):
    chamada = (
        ChamadaPainel.objects
        .filter(
            acolhimento=acolhimento,
            setor=ChamadaPainel.MEDICO,
            tipo=ChamadaPainel.CHAMADA,
        )
        .exclude(local_destino="")
        .order_by("-id")
        .first()
    )

    return chamada.local_destino if chamada else "Consultorio medico"


def registrar_transferencia_medico(
    consulta,
    medico_novo,
    crm_novo="",
    motivo="OUTRO",
    observacao="",
    medico_anterior=None,
    crm_anterior=None,
):
    TransferenciaConsultaMedica.objects.create(
        consulta=consulta,
        medico_anterior=(
            consulta.medico_responsavel
            if medico_anterior is None
            else medico_anterior
        ) or "",
        crm_anterior=(
            consulta.crm_medico
            if crm_anterior is None
            else crm_anterior
        ) or "",
        medico_novo=medico_novo,
        crm_novo=crm_novo or "",
        motivo=motivo,
        observacao=observacao,
    )


def medico_dashboard(request):
    dados_impressao = buscar_dados_impressao_medico(request)
    nome_medico = nome_usuario(request)
    crm_medico_atual = registro_profissional_request(request)
    periodo_inicio, periodo_fim = periodo_do_dia(timezone.now())
    consultorio_atual = consultorio_medico_atual(request)

    acolhimentos = (
        Acolhimento.objects
        .select_related("paciente", "classificacao", "consulta_medica")
        .prefetch_related("tempos_setores")
        .filter(
            data_acolhimento__gte=periodo_inicio,
            data_acolhimento__lte=periodo_fim,
            status__in=["CONSULTA", "RETORNO_MEDICO"],
        )
        .order_by("data_acolhimento")
    )

    minhas_consultas = (
        ConsultaMedica.objects
        .select_related(
            "acolhimento",
            "acolhimento__paciente",
            "acolhimento__classificacao"
        )
        .filter(
            acolhimento__data_acolhimento__gte=periodo_inicio,
            acolhimento__data_acolhimento__lte=periodo_fim,
            medico_responsavel=nome_medico,
        )
        .order_by("-data_consulta")
    )

    consultas_ativas = (
        ConsultaMedica.objects
        .select_related(
            "acolhimento",
            "acolhimento__paciente",
            "acolhimento__classificacao"
        )
        .filter(
            acolhimento__data_acolhimento__gte=periodo_inicio,
            acolhimento__data_acolhimento__lte=periodo_fim,
        )
        .exclude(acolhimento__status__in=["FINALIZADO", "AUSENTE"])
        .order_by("-data_consulta")
    )
    ausentes_medico = (
        Acolhimento.objects
        .select_related("paciente", "classificacao", "consulta_medica")
        .prefetch_related("tempos_setores")
        .filter(
            data_acolhimento__gte=periodo_inicio,
            data_acolhimento__lte=periodo_fim,
            status="AUSENTE",
        )
        .filter(
            Q(status_antes_ausencia__in=["CONSULTA", "RETORNO_MEDICO"])
            | Q(
                status_antes_ausencia="",
                chamadas_painel__setor=ChamadaPainel.MEDICO,
                chamadas_painel__tipo=ChamadaPainel.AUSENCIA,
            )
        )
        .distinct()
        .order_by("-data_ausente", "data_acolhimento")
    )
    acolhimentos = anexar_entrada_setor(acolhimentos, "MEDICO")
    anexar_status_chamadas(acolhimentos, ChamadaPainel.MEDICO)
    anexar_trava_medica_acolhimentos(acolhimentos, nome_medico)
    anexar_trava_medica_consultas(minhas_consultas, nome_medico)
    anexar_trava_medica_consultas(consultas_ativas, nome_medico)

    return render(
        request,
        "medico/dashboard.html",
        {
            "acolhimentos": acolhimentos,
            "total_consulta": len(acolhimentos),
            "minhas_consultas": minhas_consultas,
            "total_minhas_consultas": minhas_consultas.count(),
            "consultas_ativas": consultas_ativas,
            "total_consultas_ativas": consultas_ativas.count(),
            "ausentes_medico": ausentes_medico,
            "total_ausentes_medico": ausentes_medico.count(),
            "dados_impressao_medico": dados_impressao,
            "medico_atual": nome_medico,
            "crm_medico_atual": crm_medico_atual,
            "consultorio_medico_atual": consultorio_atual,
        }
    )


@require_POST
def definir_consultorio_medico(request):
    consultorio = consultorio_medico_informado(request)

    if not consultorio:
        messages.warning(
            request,
            "Informe o consultorio antes de iniciar as chamadas."
        )
        return redirect("medico_dashboard")

    request.session[chave_consultorio_medico(request)] = consultorio
    request.session.modified = True

    messages.success(
        request,
        f"Consultorio medico definido como {consultorio}."
    )

    return redirect("medico_dashboard")


def chamar_paciente_medico(request, acolhimento_id):
    if request.method != "POST":
        return redirect("medico_dashboard")

    consultorio = consultorio_medico_atual(request)
    medico_atual = nome_usuario(request)
    crm_medico_atual = registro_profissional_request(request)

    if not consultorio:
        messages.warning(
            request,
            "Antes de chamar pacientes, informe o consultorio onde voce esta atendendo."
        )
        return redirect("medico_dashboard")

    if not medico_atual:
        messages.warning(
            request,
            "Nao foi possivel identificar o medico logado para chamar o paciente."
        )
        return redirect("medico_dashboard")

    with transaction.atomic():
        acolhimento = get_object_or_404(
            Acolhimento.objects.select_for_update().select_related("paciente"),
            id=acolhimento_id,
            status__in=["CONSULTA", "RETORNO_MEDICO"],
        )
        consulta = (
            ConsultaMedica.objects
            .select_for_update()
            .filter(acolhimento=acolhimento)
            .first()
        )

        if not pode_editar_atendimento_medico(acolhimento, consulta, medico_atual):
            bloqueio = dados_bloqueio_atendimento_medico(
                acolhimento,
                consulta,
                medico_atual,
            )
            nome_bloqueio = (
                bloqueio["nome"]
                if bloqueio and bloqueio.get("nome")
                else "outro medico"
            )
            messages.warning(
                request,
                (
                    f"BAM {acolhimento.numero_bam} ja esta em atendimento/responsabilidade "
                    f"de {nome_bloqueio}. Para chamar, primeiro assuma o paciente."
                )
            )
            return redirect("medico_dashboard")

        chamada, total = registrar_chamada_limitada(
            ChamadaPainel.MEDICO,
            acolhimento,
            request,
            local_destino=consultorio,
        )

        if not chamada:
            messages.warning(
                request,
                f"BAM {acolhimento.numero_bam} ja foi chamado 4 vezes. Use Ausentar."
            )
            return redirect("medico_dashboard")

        marcar_atendimento_medico_em_andamento(
            acolhimento,
            medico_atual,
            crm_medico_atual,
            consultorio,
        )

        messages.success(
            request,
            f"Chamada {total}/4 registrada para o BAM {acolhimento.numero_bam} no {consultorio}."
        )

    return redirect("medico_dashboard")


def ausentar_paciente_medico(request, acolhimento_id):
    if request.method != "POST":
        return redirect("medico_dashboard")

    medico_atual = nome_usuario(request)

    with transaction.atomic():
        acolhimento = get_object_or_404(
            Acolhimento.objects.select_for_update().select_related("paciente"),
            id=acolhimento_id,
            status__in=["CONSULTA", "RETORNO_MEDICO"],
        )
        consulta = (
            ConsultaMedica.objects
            .select_for_update()
            .filter(acolhimento=acolhimento)
            .first()
        )

        if not pode_editar_atendimento_medico(acolhimento, consulta, medico_atual):
            bloqueio = dados_bloqueio_atendimento_medico(
                acolhimento,
                consulta,
                medico_atual,
            )
            nome_bloqueio = (
                bloqueio["nome"]
                if bloqueio and bloqueio.get("nome")
                else "outro medico"
            )
            messages.warning(
                request,
                (
                    f"BAM {acolhimento.numero_bam} esta em chamada por {nome_bloqueio}. "
                    "Para ausentar, primeiro assuma o paciente."
                )
            )
            return redirect("medico_dashboard")

        total = total_chamadas_setor(ChamadaPainel.MEDICO, acolhimento)

        if total < 4:
            faltam = 4 - total
            messages.warning(
                request,
                f"Para ausentar o BAM {acolhimento.numero_bam}, registre mais {faltam} chamada(s)."
            )
            return redirect("medico_dashboard")

        registrar_ausencia(
            ChamadaPainel.MEDICO,
            acolhimento,
            request,
            local_destino=ultimo_consultorio_chamado(acolhimento),
        )
        marcar_acolhimento_ausente(acolhimento)
        limpar_atendimento_medico_em_andamento(acolhimento)

        messages.warning(
            request,
            f"BAM {acolhimento.numero_bam} marcado como ausente no medico."
        )

    return redirect("medico_dashboard")


def retornar_ausente_medico(request, acolhimento_id):
    if request.method != "POST":
        return redirect("medico_dashboard")

    acolhimento = get_object_or_404(
        Acolhimento.objects.select_related("paciente"),
        id=acolhimento_id,
        status="AUSENTE",
    )
    status_retorno = acolhimento.status_antes_ausencia or "CONSULTA"

    if status_retorno not in ["CONSULTA", "RETORNO_MEDICO"]:
        messages.warning(
            request,
            f"BAM {acolhimento.numero_bam} esta ausente em outro setor."
        )
        return redirect("medico_dashboard")

    registrar_retorno(
        ChamadaPainel.MEDICO,
        acolhimento,
        request,
        local_destino=ultimo_consultorio_chamado(acolhimento),
    )
    reativar_acolhimento_ausente(acolhimento, "CONSULTA")

    messages.success(
        request,
        f"BAM {acolhimento.numero_bam} retornou para a fila medica."
    )

    return redirect("medico_dashboard")


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


def descricao_cid_codigo(codigo):
    codigo = (codigo or "").strip()

    if not codigo:
        return ""

    cid = CID.objects.filter(codigo__iexact=codigo).first()

    if cid:
        return f"{cid.codigo} - {cid.descricao}"

    return ""


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
        "alergia": (
            classificacao.alergia
            if classificacao and classificacao.alergia
            else ""
        ),
        "usoMedicamento": (
            classificacao.uso_medicamento
            if classificacao and classificacao.uso_medicamento
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
    reavaliacoes = list(consulta.reavaliacoes.all())

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
        "receita": consulta.receita or "",
        "atestado": consulta.atestado or "",
        "atestadoDias": consulta.atestado_dias or "",
        "atestadoCid": consulta.atestado_cid or "",
        "atestadoCidDescricao": descricao_cid_codigo(consulta.atestado_cid),
        "resultadoLaboratorio": consulta.resultado_exames_laboratoriais or "",
        "dataResultadoLaboratorio": formatar_data_hora(consulta.data_resultado_laboratorio),
        "tecnicoLaboratorioNome": consulta.tecnico_laboratorio_nome or "",
        "tecnicoLaboratorioRegistro": consulta.tecnico_laboratorio_registro or "",
        "resultadoImagem": consulta.resultado_exames_imagem or "",
        "dataResultadoImagem": formatar_data_hora(consulta.data_resultado_imagem),
        "resultadoRaiox": consulta.resultado_raiox or "",
        "dataResultadoRaiox": formatar_data_hora(consulta.data_resultado_raiox),
        "tecnicoRaioxNome": consulta.tecnico_raiox_nome or "",
        "tecnicoRaioxRegistro": consulta.tecnico_raiox_registro or "",
        "resultadoTomografia": consulta.resultado_tomografia or "",
        "dataResultadoTomografia": formatar_data_hora(consulta.data_resultado_tomografia),
        "tecnicoTomografiaNome": consulta.tecnico_tomografia_nome or "",
        "tecnicoTomografiaRegistro": consulta.tecnico_tomografia_registro or "",
        "resultadoMamografia": consulta.resultado_mamografia or "",
        "dataResultadoMamografia": formatar_data_hora(consulta.data_resultado_mamografia),
        "tecnicoMamografiaNome": consulta.tecnico_mamografia_nome or "",
        "tecnicoMamografiaRegistro": consulta.tecnico_mamografia_registro or "",
        "resultadoDensitometria": consulta.resultado_densitometria or "",
        "dataResultadoDensitometria": formatar_data_hora(consulta.data_resultado_densitometria),
        "tecnicoDensitometriaNome": consulta.tecnico_densitometria_nome or "",
        "tecnicoDensitometriaRegistro": consulta.tecnico_densitometria_registro or "",
        "medicamentosDispensados": consulta.medicamentos_dispensados or "",
        "profissionalFarmaciaNome": consulta.profissional_farmacia_nome or "",
        "profissionalFarmaciaRegistro": consulta.profissional_farmacia_registro or "",
        "medicacaoAdministrada": consulta.medicacao_administrada or "",
        "observacoesMedicacao": consulta.observacoes_medicacao or "",
        "profissionalMedicacaoNome": consulta.profissional_medicacao_nome or "",
        "profissionalMedicacaoRegistro": consulta.profissional_medicacao_registro or "",
        "farmaciaLiberada": consulta.farmacia_liberada,
        "reavaliacoes": [
            {
                "medico": reavaliacao.medico_responsavel or "",
                "crm": reavaliacao.crm_medico or "",
                "cid": reavaliacao.cid or "",
                "avaliacao": reavaliacao.avaliacao or "",
                "conduta": reavaliacao.get_conduta_display(),
                "orientacoes": reavaliacao.orientacoes or "",
                "data": formatar_data_hora(reavaliacao.data_reavaliacao),
            }
            for reavaliacao in reavaliacoes
        ],
        "imprimirTudo": (
            consulta.conduta in ["ALTA", "INTERNACAO"]
            or any(
                reavaliacao.conduta in ["ALTA", "INTERNACAO"]
                for reavaliacao in reavaliacoes
            )
        ),
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


def status_por_conduta_medica(conduta):
    if conduta == "ALTA":
        return "FINALIZADO"

    if conduta == "INTERNACAO":
        return "INTERNACAO"

    if conduta == "OBSERVACAO":
        return "OBSERVACAO"

    return "RETORNO_MEDICO"


def pendencias_alta_medica(consulta):
    pendencias = []

    if not consulta:
        return pendencias

    if consulta.solicita_medicacao:
        if not consulta.medicacao_realizada:
            pendencias.append("administracao da medicacao")

    if (
        consulta.solicita_exames_laboratoriais
        and not consulta.exames_laboratoriais_realizados
    ):
        pendencias.append("resultado dos exames laboratoriais")

    if (
        consulta.solicita_exames_imagem
        and not consulta.todos_exames_imagem_finalizados()
    ):
        pendencias.append("resultado dos exames de imagem")

    return pendencias


def mensagem_alta_bloqueada(pendencias):
    return (
        "Nao e possivel dar alta enquanto existir procedimento pendente: "
        f"{', '.join(pendencias)}."
    )


def atender_paciente(request, acolhimento_id):

    medico_atual = nome_usuario(request)
    crm_medico_atual = registro_profissional_request(request)
    consultorio_atual = consultorio_medico_atual(request)

    with transaction.atomic():
        acolhimento = get_object_or_404(
            Acolhimento.objects.select_for_update(),
            id=acolhimento_id
        )

        consulta = (
            ConsultaMedica.objects
            .select_for_update()
            .filter(acolhimento=acolhimento)
            .first()
        )

        pode_editar_consulta = pode_editar_atendimento_medico(
            acolhimento,
            consulta,
            medico_atual,
        )

        if pode_editar_consulta and consultorio_atual:
            marcar_atendimento_medico_em_andamento(
                acolhimento,
                medico_atual,
                crm_medico_atual,
                consultorio_atual,
            )

    if (
        not consultorio_atual
        and acolhimento.status in ["CONSULTA", "RETORNO_MEDICO"]
    ):
        messages.warning(
            request,
            "Informe o consultorio antes de atender pacientes."
        )
        return redirect("medico_dashboard")

    try:
        classificacao = acolhimento.classificacao
    except ObjectDoesNotExist:
        classificacao = None

    bloqueio_edicao_medica = dados_bloqueio_atendimento_medico(
        acolhimento,
        consulta,
        medico_atual,
    )

    if request.method == "POST" and not pode_editar_consulta:
        bloqueio_nome = (
            bloqueio_edicao_medica["nome"]
            if bloqueio_edicao_medica
            else "outro medico"
        )
        messages.error(
            request,
            (
                f"Este paciente esta em atendimento/responsabilidade de {bloqueio_nome}. "
                "Para editar, primeiro use o botao Assumir paciente."
            )
        )
        return redirect("atender_paciente", acolhimento_id=acolhimento.id)

    reavaliacao_form = ReavaliacaoMedicaForm(initial={
        "medico_responsavel": medico_atual,
        "crm_medico": crm_medico_atual,
        "conduta": "RETORNO",
    })

    if request.method == "POST" and request.POST.get("acao") == "reavaliacao":
        if not consulta:
            messages.warning(
                request,
                "Ainda nao existe consulta medica anterior para reavaliar."
            )
            return redirect("atender_paciente", acolhimento_id=acolhimento.id)

        if acolhimento.status in ["FINALIZADO", "AUSENTE"]:
            messages.warning(
                request,
                "Paciente finalizado ou ausente nao pode receber nova reavaliacao."
            )
            return redirect("medico_dashboard")

        reavaliacao_form = ReavaliacaoMedicaForm(request.POST)

        if reavaliacao_form.is_valid():
            reavaliacao = reavaliacao_form.save(commit=False)
            reavaliacao.consulta = consulta

            pendencias = pendencias_alta_medica(consulta)

            if reavaliacao.conduta == "ALTA" and pendencias:
                mensagem = mensagem_alta_bloqueada(pendencias)
                reavaliacao_form.add_error("conduta", mensagem)
                messages.error(request, mensagem)
            else:
                reavaliacao.save()

                campos_consulta = []

                if consulta.conduta != reavaliacao.conduta:
                    consulta.conduta = reavaliacao.conduta
                    campos_consulta.append("conduta")

                if reavaliacao.cid and consulta.cid != reavaliacao.cid:
                    consulta.cid = reavaliacao.cid
                    campos_consulta.append("cid")

                if (
                    reavaliacao.medico_responsavel
                    and (
                        consulta.medico_responsavel != reavaliacao.medico_responsavel
                        or (consulta.crm_medico or "") != (reavaliacao.crm_medico or "")
                    )
                ):
                    registrar_transferencia_medico(
                        consulta,
                        reavaliacao.medico_responsavel,
                        reavaliacao.crm_medico or "",
                        motivo="OUTRO",
                        observacao="Responsavel alterado ao salvar reavaliacao medica.",
                    )
                    consulta.medico_responsavel = reavaliacao.medico_responsavel
                    consulta.crm_medico = reavaliacao.crm_medico or ""
                    campos_consulta.extend(["medico_responsavel", "crm_medico"])

                if campos_consulta:
                    consulta.save(update_fields=campos_consulta)

                acolhimento.status = status_por_conduta_medica(reavaliacao.conduta)
                acolhimento.save(update_fields=["status"])

                if reavaliacao.conduta in ["ALTA", "INTERNACAO"]:
                    request.session["medico_impressao_consulta_id"] = consulta.id

                messages.success(
                    request,
                    "Reavaliacao medica registrada. Paciente encaminhado conforme a nova conduta."
                )

                return redirect("medico_dashboard")

        form = ConsultaMedicaForm(
            instance=consulta,
            initial={"queixa_principal": classificacao.queixa_principal}
            if classificacao and not consulta
            else None,
        )

    elif request.method == "POST":

        form = ConsultaMedicaForm(
            request.POST,
            instance=consulta
        )

        medico_anterior = consulta.medico_responsavel if consulta else ""
        crm_anterior = consulta.crm_medico if consulta else ""

        if form.is_valid():

            consulta_medica = form.save(commit=False)
            consulta_medica.acolhimento = acolhimento
            pendencias_alta = pendencias_alta_medica(consulta_medica)
            alta_bloqueada = (
                consulta_medica.conduta == "ALTA"
                and bool(pendencias_alta)
            )

            if alta_bloqueada:
                consulta_medica.conduta = "RETORNO"

            try:
                consulta_medica.save()
            except IntegrityError:
                messages.error(
                    request,
                    (
                        "Outro medico iniciou ou salvou esta consulta agora. "
                        "Atualize a tela antes de continuar."
                    )
                )
                return redirect("atender_paciente", acolhimento_id=acolhimento.id)

            if consulta and (
                medico_anterior != (consulta_medica.medico_responsavel or "")
                or (crm_anterior or "") != (consulta_medica.crm_medico or "")
            ):
                registrar_transferencia_medico(
                    consulta_medica,
                    consulta_medica.medico_responsavel,
                    consulta_medica.crm_medico or "",
                    motivo="OUTRO",
                    observacao="Responsável alterado ao salvar a consulta médica.",
                    medico_anterior=medico_anterior,
                    crm_anterior=crm_anterior,
                )

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

            if alta_bloqueada:
                messages.error(
                    request,
                    (
                        mensagem_alta_bloqueada(pendencias_alta)
                        + " O paciente foi encaminhado para procedimentos."
                    )
                )
            else:
                messages.success(
                    request,
                    "Consulta médica salva com sucesso. Paciente encaminhado conforme a conduta."
                )

            return redirect("medico_dashboard")

    else:

        inicial = {}

        if classificacao:
            inicial["queixa_principal"] = classificacao.queixa_principal

        if not consulta:
            inicial["medico_responsavel"] = nome_usuario(request)

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
    historico_transferencias = (
        consulta.transferencias_medico.all()
        if consulta
        else []
    )
    reavaliacoes_medicas = (
        consulta.reavaliacoes.all()
        if consulta
        else []
    )

    if not pode_editar_consulta:
        bloquear_campos_formulario(form)
        bloquear_campos_formulario(reavaliacao_form)

    pode_assumir_consulta = bool(
        medico_atual
        and acolhimento.status not in ["FINALIZADO", "AUSENTE"]
        and not pode_editar_consulta
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
            "medico_atual": medico_atual,
            "crm_medico_atual": crm_medico_atual,
            "historico_transferencias": historico_transferencias,
            "reavaliacoes_medicas": reavaliacoes_medicas,
            "reavaliacao_form": reavaliacao_form,
            "pode_editar_consulta": pode_editar_consulta,
            "bloqueio_edicao_medica": bloqueio_edicao_medica,
            "pode_assumir_consulta": pode_assumir_consulta,
            "motivos_transferencia": TransferenciaConsultaMedica.MOTIVO_CHOICES,
            "dados_base_impressao_medico": dados_base_para_impressao(
                acolhimento,
                classificacao
            ),
        }
    )


@require_POST
def assumir_paciente(request, acolhimento_id):
    novo_medico = (
        request.POST.get("novo_medico")
        or nome_usuario(request)
        or ""
    ).strip()
    crm_novo = (request.POST.get("crm_novo") or "").strip()
    if not crm_novo:
        crm_novo = registro_profissional_request(request)
    motivo = (request.POST.get("motivo") or "PLANTAO").strip()
    observacao = (request.POST.get("observacao") or "").strip()
    motivos_validos = {
        codigo
        for codigo, _ in TransferenciaConsultaMedica.MOTIVO_CHOICES
    }

    if motivo not in motivos_validos:
        motivo = "PLANTAO"

    if not novo_medico:
        messages.error(
            request,
            "Informe o nome do médico que vai assumir o paciente."
        )
        return redirect("atender_paciente", acolhimento_id=acolhimento_id)

    with transaction.atomic():
        acolhimento = get_object_or_404(
            Acolhimento.objects.select_for_update(),
            id=acolhimento_id
        )

        consulta = (
            ConsultaMedica.objects
            .select_for_update()
            .filter(acolhimento=acolhimento)
            .first()
        )

        if acolhimento.status in ["FINALIZADO", "AUSENTE"]:
            messages.warning(
                request,
                "Paciente finalizado ou ausente nao pode ser assumido por outro medico."
            )
            return redirect("medico_dashboard")

        consultorio_atual = consultorio_medico_atual(request)

        if not consulta:
            marcar_atendimento_medico_em_andamento(
                acolhimento,
                novo_medico,
                crm_novo,
                consultorio_atual,
                reiniciar=True,
            )
            messages.success(
                request,
                f"Atendimento medico assumido por {novo_medico}."
            )
        elif (
            nomes_profissionais_iguais(consulta.medico_responsavel, novo_medico)
            and (consulta.crm_medico or "") == crm_novo
        ):
            marcar_atendimento_medico_em_andamento(
                acolhimento,
                novo_medico,
                crm_novo,
                consultorio_atual,
                reiniciar=True,
            )
            messages.info(
                request,
                "Este medico ja esta responsavel pelo paciente."
            )
        else:
            registrar_transferencia_medico(
                consulta,
                novo_medico,
                crm_novo,
                motivo=motivo,
                observacao=observacao,
            )
            consulta.medico_responsavel = novo_medico
            consulta.crm_medico = crm_novo
            consulta.save(update_fields=["medico_responsavel", "crm_medico"])

            marcar_atendimento_medico_em_andamento(
                acolhimento,
                novo_medico,
                crm_novo,
                consultorio_atual,
                reiniciar=True,
            )

            messages.success(
                request,
                f"Paciente assumido por {novo_medico}. Historico de passagem registrado."
            )

    if request.POST.get("next") == "dashboard":
        return redirect("medico_dashboard")

    return redirect("atender_paciente", acolhimento_id=acolhimento_id)


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
