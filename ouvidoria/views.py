from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AndamentoOuvidoriaForm, ManifestacaoOuvidoriaForm
from .models import AndamentoOuvidoria, ManifestacaoOuvidoria


def aplicar_filtros(queryset, request):
    busca = request.GET.get("q", "").strip()
    status = request.GET.get("status", "ativos").strip()
    tipo = request.GET.get("tipo", "").strip()
    prioridade = request.GET.get("prioridade", "").strip()

    if busca:
        queryset = queryset.filter(
            Q(protocolo__icontains=busca)
            | Q(nome_manifestante__icontains=busca)
            | Q(cpf_manifestante__icontains=busca)
            | Q(numero_bam__icontains=busca)
            | Q(paciente_nome__icontains=busca)
            | Q(titulo__icontains=busca)
            | Q(setor_envolvido__icontains=busca)
        )

    if status == "ativos":
        queryset = queryset.filter(status__in=ManifestacaoOuvidoria.STATUS_ATIVOS)
    elif status:
        queryset = queryset.filter(status=status)

    if tipo:
        queryset = queryset.filter(tipo=tipo)

    if prioridade:
        queryset = queryset.filter(prioridade=prioridade)

    return queryset, {
        "q": busca,
        "status": status,
        "tipo": tipo,
        "prioridade": prioridade,
    }


@login_required
def dashboard(request):
    hoje = timezone.now().date()
    manifestacoes = ManifestacaoOuvidoria.objects.select_related("acolhimento", "aberto_por")
    manifestacoes, filtros = aplicar_filtros(manifestacoes, request)

    abertas = ManifestacaoOuvidoria.objects.filter(status__in=ManifestacaoOuvidoria.STATUS_ATIVOS)
    tipos = dict(ManifestacaoOuvidoria.TIPO_CHOICES)
    por_tipo = [
        {
            "rotulo": tipos.get(item["tipo"], item["tipo"] or "-"),
            "total": item["total"],
        }
        for item in (
            ManifestacaoOuvidoria.objects
            .values("tipo")
            .annotate(total=Count("id"))
            .order_by("-total", "tipo")[:8]
        )
    ]
    por_setor = (
        ManifestacaoOuvidoria.objects
        .exclude(setor_envolvido="")
        .values("setor_envolvido")
        .annotate(total=Count("id"))
        .order_by("-total", "setor_envolvido")[:8]
    )

    contexto = {
        "manifestacoes": manifestacoes[:150],
        "filtros": filtros,
        "status_choices": ManifestacaoOuvidoria.STATUS_CHOICES,
        "tipo_choices": ManifestacaoOuvidoria.TIPO_CHOICES,
        "prioridade_choices": ManifestacaoOuvidoria.PRIORIDADE_CHOICES,
        "total_abertas": abertas.count(),
        "total_vencidas": abertas.filter(prazo_resposta__lt=hoje).count(),
        "total_vence_hoje": abertas.filter(prazo_resposta=hoje).count(),
        "total_concluidas": ManifestacaoOuvidoria.objects.filter(status=ManifestacaoOuvidoria.CONCLUIDA).count(),
        "total_criticas": abertas.filter(prioridade=ManifestacaoOuvidoria.CRITICA).count(),
        "por_tipo": por_tipo,
        "por_setor": por_setor,
        "ultimos_andamentos": (
            AndamentoOuvidoria.objects
            .select_related("manifestacao")
            .order_by("-criado_em")[:10]
        ),
    }

    return render(request, "ouvidoria/dashboard.html", contexto)


@login_required
def formulario(request, manifestacao_id=None):
    manifestacao = None
    if manifestacao_id:
        manifestacao = get_object_or_404(ManifestacaoOuvidoria, id=manifestacao_id)

    if request.method == "POST":
        form = ManifestacaoOuvidoriaForm(request.POST, instance=manifestacao, request=request)
        if form.is_valid():
            nova = manifestacao is None
            manifestacao = form.save(commit=False)
            if nova:
                manifestacao.aberto_por = request.user
            manifestacao.save()

            AndamentoOuvidoria.objects.create(
                manifestacao=manifestacao,
                status=manifestacao.status,
                anotacao="Manifestacao cadastrada." if nova else "Manifestacao atualizada.",
                profissional_nome=manifestacao.responsavel_nome,
                profissional_registro=manifestacao.responsavel_registro,
                criado_por=request.user,
            )

            messages.success(request, f"Manifestacao {manifestacao.protocolo} salva com sucesso.")
            return redirect("ouvidoria_editar", manifestacao_id=manifestacao.id)
    else:
        form = ManifestacaoOuvidoriaForm(instance=manifestacao, request=request)

    contexto = {
        "manifestacao": manifestacao,
        "form": form,
        "andamento_form": AndamentoOuvidoriaForm(request=request),
        "andamentos": manifestacao.andamentos.all()[:30] if manifestacao else [],
    }

    return render(request, "ouvidoria/form.html", contexto)


@login_required
@require_POST
def registrar_andamento(request, manifestacao_id):
    manifestacao = get_object_or_404(ManifestacaoOuvidoria, id=manifestacao_id)
    form = AndamentoOuvidoriaForm(request.POST, request=request)

    if form.is_valid():
        andamento = form.save(commit=False)
        andamento.manifestacao = manifestacao
        andamento.criado_por = request.user
        andamento.save()

        if andamento.status:
            manifestacao.status = andamento.status
            manifestacao.responsavel_nome = andamento.profissional_nome or manifestacao.responsavel_nome
            manifestacao.responsavel_registro = andamento.profissional_registro or manifestacao.responsavel_registro
            manifestacao.save(
                update_fields=[
                    "status",
                    "responsavel_nome",
                    "responsavel_registro",
                    "respondido_em",
                    "concluido_em",
                    "atualizado_em",
                ]
            )

        messages.success(request, "Andamento registrado.")
    else:
        messages.error(request, "Nao foi possivel registrar o andamento. Confira os campos.")

    return redirect("ouvidoria_editar", manifestacao_id=manifestacao.id)
