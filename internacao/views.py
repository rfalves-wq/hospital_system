from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from acolhimento.models import Acolhimento
from acolhimento.tempos import anexar_entrada_setor
from acolhimento.utils import periodo_do_dia
from accounts.utils import nome_profissional_request

from .forms import (
    AltaInternacaoForm,
    EvolucaoInternacaoForm,
    InternacaoForm,
    LeitoInternacaoForm,
    SetorInternacaoForm,
)
from .models import Internacao, LeitoInternacao, SetorInternacao


LEITOS_PADRAO = {
    "Clinica medica": [f"CM-{numero:02d}" for numero in range(1, 13)],
    "Observacao": [f"OBS-{numero:02d}" for numero in range(1, 9)],
    "Isolamento": [f"ISO-{numero:02d}" for numero in range(1, 5)],
}


def nome_paciente(acolhimento):
    if acolhimento.paciente:
        return acolhimento.paciente.nome_completo

    return acolhimento.nome_paciente


def nome_usuario(request):
    return nome_profissional_request(request)


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


def chave_leito(valor, setor=""):
    codigo = (valor or "").strip().upper()
    setor = (setor or "").strip().upper()

    if setor:
        return f"{setor}::{codigo}"

    return codigo


def chave_leito_cadastrado(leito_id):
    return f"LEITO:{leito_id}"


def chaves_internacao(internacao):
    if internacao.leito_ref_id:
        yield chave_leito_cadastrado(internacao.leito_ref_id)

    if internacao.leito:
        yield chave_leito(internacao.leito, internacao.setor)
        yield chave_leito(internacao.leito)


def resumo_leito_ocupado(internacao):
    codigo = internacao.leito or "Sem leito"
    setor = internacao.setor or "Internacao"

    if internacao.leito_ref_id:
        codigo = internacao.leito_ref.codigo
        setor = internacao.leito_ref.setor.nome

    return {
        "codigo": codigo,
        "status": "ocupado",
        "paciente": nome_paciente(internacao.acolhimento),
        "bam": internacao.acolhimento.numero_bam or "",
        "setor": setor,
    }


def resumo_leito_vago(codigo, setor):
    return {
        "codigo": codigo,
        "status": "vago",
        "paciente": "",
        "bam": "",
        "setor": setor,
    }


def montar_mapa_leitos(internacoes):
    internacoes = list(internacoes)
    ocupados_por_leito = {}
    for internacao in internacoes:
        for chave in chaves_internacao(internacao):
            if chave:
                ocupados_por_leito[chave] = internacao

    leitos_usados = set()
    grupos = []
    leitos_cadastrados = list(
        LeitoInternacao.objects
        .select_related("setor")
        .filter(
            setor__ativo=True,
            status_operacional=LeitoInternacao.ATIVO,
        )
        .order_by("setor__ordem", "setor__nome", "ordem", "codigo")
    )

    if leitos_cadastrados:
        setores = {}
        for leito in leitos_cadastrados:
            setores.setdefault(leito.setor.nome, []).append(leito)

        for setor, leitos_do_setor in setores.items():
            leitos = []
            for leito in leitos_do_setor:
                chaves = [
                    chave_leito_cadastrado(leito.id),
                    chave_leito(leito.codigo, setor),
                    chave_leito(leito.codigo),
                ]
                internacao = next(
                    (
                        ocupados_por_leito.get(chave)
                        for chave in chaves
                        if ocupados_por_leito.get(chave)
                    ),
                    None,
                )

                if internacao:
                    leitos.append(resumo_leito_ocupado(internacao))
                    leitos_usados.update(chaves)
                else:
                    leitos.append(resumo_leito_vago(leito.codigo, setor))

            grupos.append({"setor": setor, "leitos": leitos})
    else:
        for setor, codigos in LEITOS_PADRAO.items():
            leitos = []
            for codigo in codigos:
                chaves = [chave_leito(codigo, setor), chave_leito(codigo)]
                internacao = next(
                    (
                        ocupados_por_leito.get(chave)
                        for chave in chaves
                        if ocupados_por_leito.get(chave)
                    ),
                    None,
                )

                if internacao:
                    leitos.append(resumo_leito_ocupado(internacao))
                    leitos_usados.update(chaves)
                else:
                    leitos.append(resumo_leito_vago(codigo, setor))

            grupos.append({"setor": setor, "leitos": leitos})

    ocupados_extras = []
    for internacao in internacoes:
        if any(chave in leitos_usados for chave in chaves_internacao(internacao)):
            continue

        ocupados_extras.append(resumo_leito_ocupado(internacao))

    if ocupados_extras:
        grupos.append(
            {
                "setor": "Outros leitos em uso",
                "leitos": ocupados_extras,
            }
        )

    total_ocupados = len(internacoes)
    total_vagos = sum(
        1
        for grupo in grupos
        for leito in grupo["leitos"]
        if leito["status"] == "vago"
    )

    return {
        "grupos": grupos,
        "total_ocupados": total_ocupados,
        "total_vagos": total_vagos,
    }


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
        "profissionalRegistro": evolucao.profissional_registro or "",
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
        "profissionalResponsavelRegistro": internacao.profissional_responsavel_registro or "",
        "observacoes": internacao.observacoes or "",
        "dataAlta": formatar_data_hora(internacao.data_alta),
        "resumoAlta": internacao.resumo_alta or "",
        "profissionalAlta": internacao.profissional_alta or "",
        "profissionalAltaRegistro": internacao.profissional_alta_registro or "",
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
                "leito_ref",
                "leito_ref__setor",
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
    periodo_inicio, periodo_fim = periodo_do_dia(timezone.now())
    dados_impressao = buscar_dados_impressao_internacao(request)

    aguardando_internacao = (
        Acolhimento.objects
        .select_related("paciente", "classificacao", "consulta_medica")
        .prefetch_related("tempos_setores")
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
            "leito_ref",
            "leito_ref__setor",
        )
        .prefetch_related("evolucoes")
        .filter(status="INTERNADO")
        .order_by("data_internacao")
    )

    altas_hoje = (
        Internacao.objects
        .exclude(status="INTERNADO")
        .filter(data_alta__gte=periodo_inicio, data_alta__lte=periodo_fim)
        .count()
    )

    historico = (
        Internacao.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .exclude(status="INTERNADO")
        .order_by("-data_alta", "-data_internacao")[:50]
    )

    aguardando_internacao = anexar_entrada_setor(
        aguardando_internacao,
        "INTERNACAO",
    )
    mapa_leitos = montar_mapa_leitos(internacoes_ativas)

    return render(
        request,
        "internacao/dashboard.html",
        {
            "aguardando_internacao": aguardando_internacao,
            "internacoes_ativas": internacoes_ativas,
            "historico": historico,
            "total_aguardando": len(aguardando_internacao),
            "total_internados": internacoes_ativas.count(),
            "total_altas_hoje": altas_hoje,
            "mapa_leitos": mapa_leitos,
            "total_leitos_vagos": mapa_leitos["total_vagos"],
            "total_leitos_ocupados": mapa_leitos["total_ocupados"],
            "dados_impressao_internacao": dados_impressao,
        }
    )


def leitos_ocupados_por_id():
    return {
        internacao.leito_ref_id: internacao
        for internacao in (
            Internacao.objects
            .select_related("acolhimento", "acolhimento__paciente")
            .filter(status="INTERNADO", leito_ref__isnull=False)
        )
    }


def aplicar_filtros_leitos(queryset, request, ocupados):
    busca = (request.GET.get("q") or "").strip()
    setor_id = (request.GET.get("setor") or "").strip()
    status = (request.GET.get("status") or "").strip()
    ocupacao = (request.GET.get("ocupacao") or "").strip()

    if busca:
        queryset = queryset.filter(
            Q(codigo__icontains=busca)
            | Q(observacao__icontains=busca)
            | Q(setor__nome__icontains=busca)
        )

    if setor_id:
        queryset = queryset.filter(setor_id=setor_id)

    if status:
        queryset = queryset.filter(status_operacional=status)

    leitos = list(queryset)

    if ocupacao == "ocupados":
        leitos = [leito for leito in leitos if leito.id in ocupados]
    elif ocupacao == "vagos":
        leitos = [
            leito
            for leito in leitos
            if leito.status_operacional == LeitoInternacao.ATIVO
            and leito.id not in ocupados
        ]

    for leito in leitos:
        leito.internacao_atual = ocupados.get(leito.id)
        leito.ocupado = leito.internacao_atual is not None

    return leitos, {
        "q": busca,
        "setor": setor_id,
        "status": status,
        "ocupacao": ocupacao,
    }


def gestao_leitos(request):
    setor_edicao = None
    leito_edicao = None

    if request.method == "POST":
        form_tipo = request.POST.get("form_tipo")

        if form_tipo == "setor":
            setor_id = request.POST.get("setor_id")
            if setor_id:
                setor_edicao = get_object_or_404(SetorInternacao, id=setor_id)

            setor_form = SetorInternacaoForm(request.POST, instance=setor_edicao)
            leito_form = LeitoInternacaoForm()

            if setor_form.is_valid():
                setor = setor_form.save()
                messages.success(request, f"Setor {setor.nome} salvo com sucesso.")
                return redirect("gestao_leitos")

            messages.error(request, "Confira os dados do setor.")

        elif form_tipo == "leito":
            leito_id = request.POST.get("leito_id")
            if leito_id:
                leito_edicao = get_object_or_404(LeitoInternacao, id=leito_id)

            setor_form = SetorInternacaoForm()
            leito_form = LeitoInternacaoForm(request.POST, instance=leito_edicao)

            if leito_form.is_valid():
                leito = leito_form.save()
                messages.success(request, f"Leito {leito.codigo} salvo com sucesso.")
                return redirect("gestao_leitos")

            messages.error(request, "Confira os dados do leito.")

        else:
            setor_form = SetorInternacaoForm()
            leito_form = LeitoInternacaoForm()
            messages.warning(request, "Acao invalida.")
    else:
        editar_setor = request.GET.get("editar_setor")
        editar_leito = request.GET.get("editar_leito")

        if editar_setor:
            setor_edicao = get_object_or_404(SetorInternacao, id=editar_setor)

        if editar_leito:
            leito_edicao = get_object_or_404(
                LeitoInternacao.objects.select_related("setor"),
                id=editar_leito,
            )

        setor_form = SetorInternacaoForm(instance=setor_edicao)
        leito_form = LeitoInternacaoForm(instance=leito_edicao)

    setores = (
        SetorInternacao.objects
        .annotate(total_leitos=Count("leitos"))
        .order_by("ordem", "nome")
    )
    ocupados = leitos_ocupados_por_id()
    leitos_queryset = (
        LeitoInternacao.objects
        .select_related("setor")
        .order_by("setor__ordem", "setor__nome", "ordem", "codigo")
    )
    leitos, filtros = aplicar_filtros_leitos(leitos_queryset, request, ocupados)
    total_ativos = LeitoInternacao.objects.filter(
        status_operacional=LeitoInternacao.ATIVO,
        setor__ativo=True,
    ).count()
    total_ocupados = len(ocupados)

    contexto = {
        "setor_form": setor_form,
        "leito_form": leito_form,
        "setor_edicao": setor_edicao,
        "leito_edicao": leito_edicao,
        "setores": setores,
        "leitos": leitos,
        "filtros": filtros,
        "status_choices": LeitoInternacao.STATUS_OPERACIONAL_CHOICES,
        "total_setores": SetorInternacao.objects.count(),
        "total_leitos": LeitoInternacao.objects.count(),
        "total_ativos": total_ativos,
        "total_ocupados": total_ocupados,
        "total_vagos": max(total_ativos - total_ocupados, 0),
        "total_manutencao": LeitoInternacao.objects.filter(
            status_operacional=LeitoInternacao.MANUTENCAO,
        ).count(),
        "total_bloqueados": LeitoInternacao.objects.filter(
            status_operacional=LeitoInternacao.BLOQUEADO,
        ).count(),
    }

    return render(request, "internacao/leitos.html", contexto)


@require_POST
def alterar_status_leito(request, leito_id):
    leito = get_object_or_404(LeitoInternacao, id=leito_id)
    novo_status = request.POST.get("status_operacional")
    status_validos = {
        codigo
        for codigo, _rotulo in LeitoInternacao.STATUS_OPERACIONAL_CHOICES
    }

    if novo_status not in status_validos:
        messages.error(request, "Status de leito invalido.")
        return redirect("gestao_leitos")

    internacao = (
        Internacao.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .filter(status="INTERNADO", leito_ref=leito)
        .first()
    )

    if internacao and novo_status != LeitoInternacao.ATIVO:
        messages.error(
            request,
            "Nao e possivel bloquear ou colocar em manutencao um leito ocupado.",
        )
        return redirect("gestao_leitos")

    leito.status_operacional = novo_status
    leito.save(update_fields=["status_operacional", "atualizado_em"])
    messages.success(request, f"Status do leito {leito.codigo} atualizado.")

    return redirect("gestao_leitos")


@require_POST
def alterar_status_setor(request, setor_id):
    setor = get_object_or_404(SetorInternacao, id=setor_id)
    ativar = request.POST.get("ativo") == "1"

    if not ativar and Internacao.objects.filter(
        status="INTERNADO",
        leito_ref__setor=setor,
    ).exists():
        messages.error(
            request,
            "Nao e possivel desativar um setor com paciente internado.",
        )
        return redirect("gestao_leitos")

    setor.ativo = ativar
    setor.save(update_fields=["ativo"])

    if setor.ativo:
        messages.success(request, f"Setor {setor.nome} ativado.")
    else:
        messages.warning(request, f"Setor {setor.nome} desativado.")

    return redirect("gestao_leitos")


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
            leito_informado = (form.cleaned_data.get("leito") or "").strip()
            setor_informado = (form.cleaned_data.get("setor") or "").strip()
            leito_em_uso = Internacao.objects.filter(status="INTERNADO")

            if setor_informado:
                leito_em_uso = leito_em_uso.filter(
                    Q(leito__iexact=leito_informado, setor__iexact=setor_informado)
                    | Q(
                        leito_ref__codigo__iexact=leito_informado,
                        leito_ref__setor__nome__iexact=setor_informado,
                    )
                )
            else:
                leito_em_uso = leito_em_uso.filter(
                    Q(leito__iexact=leito_informado)
                    | Q(leito_ref__codigo__iexact=leito_informado)
                )

            if internacao and internacao.id:
                leito_em_uso = leito_em_uso.exclude(id=internacao.id)

            if leito_em_uso.exists():
                form.add_error("leito", "Este leito ja esta ocupado por outro paciente.")
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

            internacao = form.save(commit=False)
            internacao.acolhimento = acolhimento
            internacao.status = "INTERNADO"
            internacao.data_alta = None
            internacao.resumo_alta = ""
            internacao.profissional_alta = ""
            internacao.profissional_alta_registro = ""
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
        leito_param = (request.GET.get("leito") or "").strip()
        setor_param = (request.GET.get("setor") or "").strip()

        if leito_param:
            initial["leito"] = leito_param

        if setor_param:
            initial["setor"] = setor_param

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
            "leito_ref",
            "leito_ref__setor",
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
