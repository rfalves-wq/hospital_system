from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import Usuario

from .forms import EscalaFuncionarioForm, FuncionarioForm, VinculoFuncionarioForm
from .models import EscalaFuncionario, Funcionario


def aplicar_filtros(queryset, request):
    busca = request.GET.get("q", "").strip()
    setor = request.GET.get("setor", "").strip()
    status = request.GET.get("status", "ativos")

    if busca:
        queryset = queryset.filter(
            Q(nome__icontains=busca)
            | Q(cpf__icontains=busca)
            | Q(matricula__icontains=busca)
            | Q(cargo__icontains=busca)
            | Q(funcao__icontains=busca)
            | Q(registro_profissional__icontains=busca)
            | Q(usuario__username__icontains=busca)
        )

    if setor:
        queryset = queryset.filter(setor=setor)

    if status == "ativos":
        queryset = queryset.filter(ativo=True)
    elif status == "inativos":
        queryset = queryset.filter(ativo=False)
    elif status == "sem_login":
        queryset = queryset.filter(usuario__isnull=True)
    elif status == "sem_conselho":
        queryset = queryset.filter(
            Q(conselho_profissional="")
            | Q(registro_profissional="")
        )

    return queryset, {
        "q": busca,
        "setor": setor,
        "status": status,
    }


def usuarios_sem_funcionario():
    return Usuario.objects.filter(cadastro_funcionario__isnull=True).order_by(
        "first_name",
        "username",
    )


@login_required
def dashboard(request):
    if request.method == "POST":
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            funcionario = form.save()
            messages.success(request, f"Funcionario {funcionario.nome} cadastrado.")
            return redirect("funcionarios_dashboard")
    else:
        form = FuncionarioForm()

    funcionarios = Funcionario.objects.select_related("usuario", "unidade")
    funcionarios, filtros = aplicar_filtros(funcionarios, request)
    hoje = timezone.now().date()

    contexto = {
        "form": form,
        "funcionarios": funcionarios[:150],
        "filtros": filtros,
        "setores": Funcionario.SETOR_CHOICES,
        "total_ativos": Funcionario.objects.filter(ativo=True).count(),
        "total_sem_login": Funcionario.objects.filter(usuario__isnull=True).count(),
        "total_sem_conselho": Funcionario.objects.filter(
            ativo=True,
        ).filter(Q(conselho_profissional="") | Q(registro_profissional="")).count(),
        "total_plantao_hoje": EscalaFuncionario.objects.filter(
            data=hoje,
        ).exclude(status=EscalaFuncionario.CANCELADA).count(),
        "total_readmitidos": Funcionario.objects.annotate(
            total_vinculos=Count("vinculos")
        ).filter(total_vinculos__gt=1).count(),
        "por_setor": (
            Funcionario.objects
            .filter(ativo=True)
            .exclude(setor="")
            .values("setor")
            .annotate(total=Count("id"))
            .order_by("-total", "setor")[:8]
        ),
        "escalas_hoje": (
            EscalaFuncionario.objects
            .select_related("funcionario")
            .filter(data=hoje)
            .exclude(status=EscalaFuncionario.CANCELADA)
            .order_by("hora_inicio", "funcionario__nome")[:12]
        ),
        "usuarios_sem_funcionario": usuarios_sem_funcionario()[:8],
    }

    return render(request, "funcionarios/dashboard.html", contexto)


@login_required
def editar(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    form = FuncionarioForm(instance=funcionario)
    escala_form = EscalaFuncionarioForm(funcionario=funcionario)
    vinculo_form = VinculoFuncionarioForm(funcionario=funcionario)

    if request.method == "POST":
        tipo_form = request.POST.get("form_tipo", "funcionario")
        if tipo_form == "escala":
            escala_form = EscalaFuncionarioForm(request.POST, funcionario=funcionario)
            if escala_form.is_valid():
                escala = escala_form.save(commit=False)
                escala.funcionario = funcionario
                escala.setor = escala.setor or funcionario.setor
                escala.setor_ref = escala.setor_ref or funcionario.setor_ref
                escala.save()
                messages.success(request, "Escala registrada com sucesso.")
                return redirect("funcionarios_editar", funcionario_id=funcionario.id)
        elif tipo_form == "vinculo":
            vinculo_form = VinculoFuncionarioForm(request.POST, funcionario=funcionario)
            if vinculo_form.is_valid():
                vinculo = vinculo_form.save(commit=False)
                vinculo.funcionario = funcionario
                vinculo.save()
                atualizar_funcionario_pelo_vinculo(funcionario, vinculo)
                messages.success(request, "Vinculo registrado no historico.")
                return redirect("funcionarios_editar", funcionario_id=funcionario.id)
        else:
            form = FuncionarioForm(request.POST, instance=funcionario)
            if form.is_valid():
                form.save()
                messages.success(request, "Funcionario atualizado com sucesso.")
                return redirect("funcionarios_dashboard")

    contexto = {
        "funcionario": funcionario,
        "form": form,
        "escala_form": escala_form,
        "vinculo_form": vinculo_form,
        "escalas": funcionario.escalas.all()[:30],
        "vinculos": funcionario.vinculos.select_related("unidade")[:30],
    }

    return render(request, "funcionarios/editar.html", contexto)


def atualizar_funcionario_pelo_vinculo(funcionario, vinculo):
    vinculo_mais_recente = funcionario.vinculos.order_by("-data_admissao", "-id").first()
    if not vinculo_mais_recente or vinculo_mais_recente.id != vinculo.id:
        return

    funcionario.data_admissao = vinculo.data_admissao
    funcionario.data_demissao = vinculo.data_demissao
    funcionario.tipo_vinculo_ref = vinculo.tipo_vinculo_ref or funcionario.tipo_vinculo_ref
    funcionario.tipo_vinculo = vinculo.tipo_vinculo or funcionario.tipo_vinculo
    funcionario.cargo_ref = vinculo.cargo_ref or funcionario.cargo_ref
    funcionario.cargo = vinculo.cargo or funcionario.cargo
    funcionario.setor_ref = vinculo.setor_ref or funcionario.setor_ref
    funcionario.setor = vinculo.setor or funcionario.setor
    funcionario.unidade = vinculo.unidade or funcionario.unidade
    funcionario.ativo = vinculo.data_demissao is None
    funcionario.save(
        update_fields=[
            "data_admissao",
            "data_demissao",
            "tipo_vinculo_ref",
            "tipo_vinculo",
            "cargo_ref",
            "cargo",
            "setor_ref",
            "setor",
            "unidade",
            "ativo",
            "atualizado_em",
        ]
    )

    if funcionario.usuario_id:
        funcionario.usuario.is_active = funcionario.ativo
        funcionario.usuario.save(update_fields=["is_active"])


@login_required
@require_POST
def alterar_status(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    funcionario.ativo = not funcionario.ativo
    funcionario.save(update_fields=["ativo", "atualizado_em"])

    if funcionario.ativo:
        messages.success(request, f"Funcionario {funcionario.nome} ativado.")
    else:
        messages.warning(request, f"Funcionario {funcionario.nome} inativado.")

    return redirect("funcionarios_dashboard")


@login_required
@require_POST
def sincronizar_logins(request):
    criados = 0

    for usuario in usuarios_sem_funcionario():
        nome = usuario.get_full_name() or usuario.username
        Funcionario.objects.create(
            usuario=usuario,
            nome=nome,
            cargo_ref=usuario.cargo_ref,
            cargo=usuario.cargo or "",
            unidade=usuario.unidade,
            conselho_ref=usuario.conselho_ref,
            conselho_profissional=usuario.conselho_profissional or "",
            registro_profissional=usuario.registro_profissional or "",
            email=usuario.email or "",
            ativo=usuario.is_active,
        )
        criados += 1

    if criados:
        messages.success(request, f"{criados} login(s) importado(s) para Funcionarios.")
    else:
        messages.info(request, "Todos os logins ja estao vinculados a funcionarios.")

    return redirect("funcionarios_dashboard")
