from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from acolhimento.models import Acolhimento

from .forms import AltaInternacaoForm, EvolucaoInternacaoForm, InternacaoForm
from .models import Internacao


def nome_paciente(acolhimento):
    if acolhimento.paciente:
        return acolhimento.paciente.nome_completo

    return acolhimento.nome_paciente


def nome_usuario(request):
    if request.user.is_authenticated:
        return request.user.get_full_name() or request.user.username

    return ""


def related_or_none(obj, attr):
    try:
        return getattr(obj, attr)
    except ObjectDoesNotExist:
        return None


def formatar_data(valor):
    return valor.strftime("%d/%m/%Y") if valor else ""


def formatar_data_hora(valor):
    return valor.strftime("%d/%m/%Y %H:%M") if valor else ""


def formatar_hora(valor):
    return valor.strftime("%H:%M") if valor else ""


def formatar_decimal(valor):
    if valor is None:
        return ""

    return str(valor).replace(".", ",")


def dados_evolucao_para_impressao(evolucao):
    return {
        "id": evolucao.id,
        "data": formatar_data_hora(evolucao.data_evolucao),
        "pressao": evolucao.pressao_arterial or "",
        "temperatura": formatar_decimal(evolucao.temperatura),
        "pulso": evolucao.pulso if evolucao.pulso is not None else "",
        "fr": (
            evolucao.frequencia_respiratoria
            if evolucao.frequencia_respiratoria is not None
            else ""
        ),
        "saturacao": evolucao.saturacao if evolucao.saturacao is not None else "",
        "evolucao": evolucao.evolucao or "",
        "conduta": evolucao.conduta or "",
        "profissional": evolucao.profissional or "",
    }


def dados_internacao_para_impressao(internacao, tipo="admissao", evolucao_id=None):
    acolhimento = internacao.acolhimento
    paciente = acolhimento.paciente
    consulta = related_or_none(acolhimento, "consulta_medica")
    classificacao = related_or_none(acolhimento, "classificacao")
    evolucoes = [
        dados_evolucao_para_impressao(evolucao)
        for evolucao in internacao.evolucoes.all()
    ]
    evolucao_impressao = None

    if evolucao_id:
        for evolucao in evolucoes:
            if evolucao["id"] == evolucao_id:
                evolucao_impressao = evolucao
                break

    if not evolucao_impressao and evolucoes:
        evolucao_impressao = evolucoes[0]

    return {
        "tipoImpressao": tipo,
        "bam": acolhimento.numero_bam or "",
        "paciente": nome_paciente(acolhimento),
        "cpf": (
            paciente.cpf
            if paciente and paciente.cpf
            else acolhimento.cpf or ""
        ),
        "nascimento": formatar_data(acolhimento.data_nascimento),
        "idade": acolhimento.idade if acolhimento.idade is not None else "",
        "statusPaciente": acolhimento.get_status_display(),
        "tipoAtendimento": acolhimento.get_tipo_atendimento_display(),
        "dataAcolhimento": formatar_data_hora(acolhimento.data_acolhimento),
        "horaChegada": (
            formatar_hora(acolhimento.hora_chegada)
            or formatar_hora(acolhimento.data_acolhimento)
        ),
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
        "medico": consulta.medico_responsavel if consulta else "",
        "crm": consulta.crm_medico if consulta else "",
        "cid": consulta.cid if consulta else "",
        "hipotese": consulta.hipotese_diagnostica if consulta else "",
        "orientacoesMedicas": consulta.orientacoes if consulta else "",
        "leito": internacao.leito or "",
        "setor": internacao.setor or "",
        "dataInternacao": formatar_data_hora(internacao.data_internacao),
        "statusInternacao": internacao.get_status_display(),
        "diagnosticoAdmissao": internacao.diagnostico_admissao or "",
        "cuidados": internacao.cuidados or "",
        "profissionalResponsavel": internacao.profissional_responsavel or "",
        "observacoes": internacao.observacoes or "",
        "dataAlta": formatar_data_hora(internacao.data_alta),
        "resumoAlta": internacao.resumo_alta or "",
        "profissionalAlta": internacao.profissional_alta or "",
        "evolucoes": evolucoes,
        "evolucaoImpressao": evolucao_impressao,
    }


def buscar_dados_impressao_internacao(request):
    internacao_id = request.session.pop("internacao_impressao_id", None)

    if not internacao_id:
        return None

    tipo = request.session.pop("internacao_impressao_tipo", "admissao")
    evolucao_id = request.session.pop("internacao_impressao_evolucao_id", None)

    try:
        internacao = (
            Internacao.objects
            .select_related(
                "acolhimento",
                "acolhimento__paciente",
                "acolhimento__classificacao",
                "acolhimento__consulta_medica",
            )
            .prefetch_related("evolucoes")
            .get(id=internacao_id)
        )
    except Internacao.DoesNotExist:
        return None

    return dados_internacao_para_impressao(
        internacao,
        tipo=tipo,
        evolucao_id=evolucao_id,
    )


def internacao_dashboard(request):
    hoje = timezone.now().date()
    dados_impressao = buscar_dados_impressao_internacao(request)

    aguardando_internacao = (
        Acolhimento.objects
        .select_related("paciente", "classificacao", "consulta_medica")
        .filter(status="INTERNACAO", internacao__isnull=True)
        .order_by("data_acolhimento")
    )

    internacoes_ativas = (
        Internacao.objects
        .select_related(
            "acolhimento",
            "acolhimento__paciente",
            "acolhimento__classificacao",
            "acolhimento__consulta_medica",
        )
        .prefetch_related("evolucoes")
        .filter(status="INTERNADO")
        .order_by("data_internacao")
    )

    altas_hoje = (
        Internacao.objects
        .exclude(status="INTERNADO")
        .filter(data_alta__date=hoje)
        .count()
    )

    historico = (
        Internacao.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .exclude(status="INTERNADO")
        .order_by("-data_alta", "-data_internacao")[:50]
    )

    return render(
        request,
        "internacao/dashboard.html",
        {
            "aguardando_internacao": aguardando_internacao,
            "internacoes_ativas": internacoes_ativas,
            "historico": historico,
            "total_aguardando": aguardando_internacao.count(),
            "total_internados": internacoes_ativas.count(),
            "total_altas_hoje": altas_hoje,
            "dados_impressao_internacao": dados_impressao,
        }
    )


def registrar_internacao(request, acolhimento_id):
    acolhimento = get_object_or_404(
        Acolhimento.objects.select_related(
            "paciente",
            "classificacao",
            "consulta_medica",
        ),
        id=acolhimento_id,
    )

    internacao = Internacao.objects.filter(acolhimento=acolhimento).first()

    if internacao and internacao.status == "INTERNADO":
        return redirect("detalhe_internacao", internacao_id=internacao.id)

    if request.method == "POST":
        form = InternacaoForm(request.POST, instance=internacao)

        if form.is_valid():
            internacao = form.save(commit=False)
            internacao.acolhimento = acolhimento
            internacao.status = "INTERNADO"
            internacao.data_alta = None
            internacao.resumo_alta = ""
            internacao.profissional_alta = ""
            internacao.save()

            acolhimento.status = "INTERNACAO"
            acolhimento.save(update_fields=["status"])

            messages.success(
                request,
                f"Internação registrada para o BAM {acolhimento.numero_bam}."
            )

            request.session["internacao_impressao_id"] = internacao.id
            request.session["internacao_impressao_tipo"] = "admissao"

            return redirect("detalhe_internacao", internacao_id=internacao.id)
    else:
        initial = {
            "profissional_responsavel": nome_usuario(request),
        }

        consulta = related_or_none(acolhimento, "consulta_medica")

        if consulta:
            initial["diagnostico_admissao"] = consulta.hipotese_diagnostica
            initial["cuidados"] = consulta.orientacoes

        form = InternacaoForm(instance=internacao, initial=initial)

    return render(
        request,
        "internacao/registrar.html",
        {
            "form": form,
            "acolhimento": acolhimento,
            "nome_paciente": nome_paciente(acolhimento),
            "consulta": related_or_none(acolhimento, "consulta_medica"),
            "classificacao": related_or_none(acolhimento, "classificacao"),
        }
    )


def detalhe_internacao(request, internacao_id):
    internacao = get_object_or_404(
        Internacao.objects.select_related(
            "acolhimento",
            "acolhimento__paciente",
            "acolhimento__classificacao",
            "acolhimento__consulta_medica",
        ).prefetch_related("evolucoes"),
        id=internacao_id,
    )
    dados_impressao = buscar_dados_impressao_internacao(request)

    if request.method == "POST":
        acao = request.POST.get("acao")

        if acao == "evoluir":
            evolucao_form = EvolucaoInternacaoForm(request.POST)
            alta_form = AltaInternacaoForm(instance=internacao)

            if evolucao_form.is_valid():
                evolucao = evolucao_form.save(commit=False)
                evolucao.internacao = internacao
                evolucao.save()

                messages.success(request, "Evolução registrada com sucesso.")
                request.session["internacao_impressao_id"] = internacao.id
                request.session["internacao_impressao_tipo"] = "evolucao"
                request.session["internacao_impressao_evolucao_id"] = evolucao.id
                return redirect("detalhe_internacao", internacao_id=internacao.id)

        elif acao == "alta":
            evolucao_form = EvolucaoInternacaoForm()
            alta_form = AltaInternacaoForm(request.POST, instance=internacao)

            if alta_form.is_valid():
                internacao = alta_form.save(commit=False)
                internacao.status = "ALTA"
                internacao.data_alta = timezone.now()
                internacao.save()

                acolhimento = internacao.acolhimento
                acolhimento.status = "FINALIZADO"
                acolhimento.save(update_fields=["status"])

                messages.success(
                    request,
                    f"Alta da internação registrada para o BAM {acolhimento.numero_bam}."
                )

                request.session["internacao_impressao_id"] = internacao.id
                request.session["internacao_impressao_tipo"] = "alta"

                return redirect("internacao_dashboard")

        else:
            messages.warning(request, "Ação inválida.")
            return redirect("detalhe_internacao", internacao_id=internacao.id)
    else:
        evolucao_form = EvolucaoInternacaoForm(initial={
            "profissional": nome_usuario(request),
        })
        alta_form = AltaInternacaoForm(instance=internacao, initial={
            "profissional_alta": nome_usuario(request),
        })

    return render(
        request,
        "internacao/detalhe.html",
        {
            "internacao": internacao,
            "acolhimento": internacao.acolhimento,
            "nome_paciente": nome_paciente(internacao.acolhimento),
            "consulta": related_or_none(internacao.acolhimento, "consulta_medica"),
            "classificacao": related_or_none(internacao.acolhimento, "classificacao"),
            "evolucao_form": evolucao_form,
            "alta_form": alta_form,
            "evolucoes": internacao.evolucoes.all(),
            "dados_internacao_atual": dados_internacao_para_impressao(
                internacao,
                tipo="completo",
            ),
            "dados_impressao_internacao": dados_impressao,
        }
    )
