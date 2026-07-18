from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, UsuarioSistemaForm
from .models import PainelSistema, PerfilAcesso, Usuario
from acolhimento.utils import periodo_do_dia
from classificacao.models import ClassificacaoRisco
from internacao.models import EvolucaoInternacao, Internacao
from medico.models import ConsultaMedica
from tecnologia.models import ChamadoManutencaoTI


def destino_seguro(request):
    destino = request.POST.get("next") or request.GET.get("next") or ""

    if destino and url_has_allowed_host_and_scheme(
        destino,
        allowed_hosts={request.get_host()},
    ):
        return destino

    return reverse("dashboard")


def login_view(request):
    if request.user.is_authenticated:
        return redirect(destino_seguro(request))

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect(destino_seguro(request))

        form.add_error(None, "Usuario ou senha invalidos.")

    return render(
        request,
        "login.html",
        {
            "form": form,
            "next": request.GET.get("next", ""),
        }
    )


def logout_view(request):
    logout(request)
    messages.info(request, "Sessao encerrada com seguranca.")
    return redirect("login")


def redirecionar_sem_permissao(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(
            request,
            "Apenas administradores podem gerenciar profissionais e acessos."
        )
        return redirect("dashboard")

    return None


def nomes_usuario_para_contagem(usuario):
    nomes = {
        (usuario.username or "").strip(),
        (usuario.get_full_name() or "").strip(),
    }
    return [nome for nome in nomes if nome]


def filtro_nome_profissional(campo, nomes):
    filtro = Q()
    for nome in nomes:
        filtro |= Q(**{f"{campo}__iexact": nome})
    return filtro


def total_por_profissional(
    modelo,
    campo_nome,
    campo_data,
    nomes,
    periodo_inicio,
    periodo_fim,
    extra=None,
):
    if not nomes:
        return 0

    filtro = filtro_nome_profissional(campo_nome, nomes)
    filtro &= Q(**{f"{campo_data}__gte": periodo_inicio})
    filtro &= Q(**{f"{campo_data}__lte": periodo_fim})

    if extra is not None:
        filtro &= extra

    return modelo.objects.filter(filtro).count()


def resumo_atendimentos_usuario_hoje(usuario, periodo_inicio, periodo_fim):
    nomes = nomes_usuario_para_contagem(usuario)

    classificacao = total_por_profissional(
        ClassificacaoRisco,
        "usuario_responsavel",
        "data_classificacao",
        nomes,
        periodo_inicio,
        periodo_fim,
    )
    medico = total_por_profissional(
        ConsultaMedica,
        "medico_responsavel",
        "data_consulta",
        nomes,
        periodo_inicio,
        periodo_fim,
    )
    medicacao = total_por_profissional(
        ConsultaMedica,
        "profissional_medicacao_nome",
        "data_medicacao",
        nomes,
        periodo_inicio,
        periodo_fim,
    )
    farmacia = total_por_profissional(
        ConsultaMedica,
        "profissional_farmacia_nome",
        "data_liberacao_farmacia",
        nomes,
        periodo_inicio,
        periodo_fim,
    )
    laboratorio = total_por_profissional(
        ConsultaMedica,
        "tecnico_laboratorio_nome",
        "data_resultado_laboratorio",
        nomes,
        periodo_inicio,
        periodo_fim,
    )
    imagem = sum(
        [
            total_por_profissional(
                ConsultaMedica,
                "tecnico_raiox_nome",
                "data_resultado_raiox",
                nomes,
                periodo_inicio,
                periodo_fim,
                Q(raiox_realizado=True),
            ),
            total_por_profissional(
                ConsultaMedica,
                "tecnico_tomografia_nome",
                "data_resultado_tomografia",
                nomes,
                periodo_inicio,
                periodo_fim,
                Q(tomografia_realizada=True),
            ),
            total_por_profissional(
                ConsultaMedica,
                "tecnico_mamografia_nome",
                "data_resultado_mamografia",
                nomes,
                periodo_inicio,
                periodo_fim,
                Q(mamografia_realizada=True),
            ),
            total_por_profissional(
                ConsultaMedica,
                "tecnico_densitometria_nome",
                "data_resultado_densitometria",
                nomes,
                periodo_inicio,
                periodo_fim,
                Q(densitometria_realizada=True),
            ),
        ]
    )
    internacao = sum(
        [
            total_por_profissional(
                Internacao,
                "profissional_responsavel",
                "data_internacao",
                nomes,
                periodo_inicio,
                periodo_fim,
            ),
            total_por_profissional(
                Internacao,
                "profissional_alta",
                "data_alta",
                nomes,
                periodo_inicio,
                periodo_fim,
            ),
            total_por_profissional(
                EvolucaoInternacao,
                "profissional",
                "data_evolucao",
                nomes,
                periodo_inicio,
                periodo_fim,
            ),
        ]
    )
    ti = total_por_profissional(
        ChamadoManutencaoTI,
        "respondido_por",
        "respondido_em",
        nomes,
        periodo_inicio,
        periodo_fim,
    )

    detalhes = [
        {"nome": "Classificacao", "total": classificacao},
        {"nome": "Medico", "total": medico},
        {"nome": "Medicacao", "total": medicacao},
        {"nome": "Farmacia", "total": farmacia},
        {"nome": "Laboratorio", "total": laboratorio},
        {"nome": "Imagem", "total": imagem},
        {"nome": "Internacao", "total": internacao},
        {"nome": "TI", "total": ti},
    ]
    total = sum(item["total"] for item in detalhes)

    return {
        "total": total,
        "detalhes": [item for item in detalhes if item["total"]],
    }


def aplicar_resumo_atendimentos_hoje(usuarios, periodo_inicio, periodo_fim):
    usuarios_com_resumo = []

    for usuario in usuarios:
        resumo = resumo_atendimentos_usuario_hoje(usuario, periodo_inicio, periodo_fim)
        usuario.atendimentos_hoje_total = resumo["total"]
        usuario.atendimentos_hoje_detalhes = resumo["detalhes"]
        usuarios_com_resumo.append(usuario)

    return usuarios_com_resumo


@login_required
def seguranca_dashboard(request):
    sem_permissao = redirecionar_sem_permissao(request)
    if sem_permissao:
        return sem_permissao

    periodo_inicio, periodo_fim = periodo_do_dia(timezone.now())
    hoje = periodo_inicio.date()
    usuarios = Usuario.objects.all()

    totais = {
        "usuarios": usuarios.count(),
        "ativos": usuarios.filter(is_active=True).count(),
        "inativos": usuarios.filter(is_active=False).count(),
        "administradores": usuarios.filter(is_superuser=True).count(),
        "equipe": usuarios.filter(is_staff=True).count(),
        "sem_acesso": usuarios.filter(
            is_staff=False,
            is_superuser=False,
            perfis_acesso__isnull=True,
            paineis_extra__isnull=True,
        ).distinct().count(),
    }

    perfis = (
        PerfilAcesso.objects
        .prefetch_related("paineis")
        .annotate(total_usuarios=Count("usuarios", distinct=True))
        .order_by("nome")
    )

    painel_resumo = []
    for painel in PainelSistema.objects.filter(ativo=True).order_by("ordem", "nome"):
        total_usuarios = usuarios.filter(
            Q(perfis_acesso__paineis=painel, perfis_acesso__ativo=True)
            | Q(paineis_extra=painel)
        ).distinct().count()
        total_extras = usuarios.filter(paineis_extra=painel).distinct().count()
        painel_resumo.append(
            {
                "painel": painel,
                "total_usuarios": total_usuarios,
                "total_extras": total_extras,
            }
        )

    usuarios_recentes = aplicar_resumo_atendimentos_hoje(
        usuarios
        .prefetch_related("perfis_acesso", "paineis_extra")
        .order_by("-date_joined")[:8],
        periodo_inicio,
        periodo_fim,
    )

    usuarios_atendimento_hoje = aplicar_resumo_atendimentos_hoje(
        Usuario.objects
        .filter(is_active=True)
        .prefetch_related("perfis_acesso")
        .order_by("first_name", "username"),
        periodo_inicio,
        periodo_fim,
    )

    return render(
        request,
        "accounts/seguranca.html",
        {
            "totais": totais,
            "perfis": perfis,
            "painel_resumo": painel_resumo,
            "usuarios_recentes": usuarios_recentes,
            "usuarios_atendimento_hoje": usuarios_atendimento_hoje,
            "data_atendimentos_hoje": hoje,
        },
    )


@login_required
def seguranca_usuarios(request):
    sem_permissao = redirecionar_sem_permissao(request)
    if sem_permissao:
        return sem_permissao

    busca = request.GET.get("q", "").strip()
    status = request.GET.get("status", "todos")

    periodo_inicio, periodo_fim = periodo_do_dia(timezone.now())
    hoje = periodo_inicio.date()
    usuarios = (
        Usuario.objects
        .prefetch_related("perfis_acesso", "paineis_extra")
        .select_related("unidade")
        .order_by("first_name", "username")
    )

    if busca:
        usuarios = usuarios.filter(
            Q(username__icontains=busca)
            | Q(first_name__icontains=busca)
            | Q(last_name__icontains=busca)
            | Q(email__icontains=busca)
            | Q(cargo__icontains=busca)
            | Q(conselho_profissional__icontains=busca)
            | Q(registro_profissional__icontains=busca)
            | Q(perfis_acesso__nome__icontains=busca)
        ).distinct()

    if status == "ativos":
        usuarios = usuarios.filter(is_active=True)
    elif status == "inativos":
        usuarios = usuarios.filter(is_active=False)
    elif status == "admin":
        usuarios = usuarios.filter(Q(is_staff=True) | Q(is_superuser=True))

    usuarios = aplicar_resumo_atendimentos_hoje(usuarios, periodo_inicio, periodo_fim)

    return render(
        request,
        "accounts/usuarios.html",
        {
            "usuarios": usuarios,
            "busca": busca,
            "status": status,
            "data_atendimentos_hoje": hoje,
        },
    )


@login_required
def seguranca_usuario_novo(request):
    sem_permissao = redirecionar_sem_permissao(request)
    if sem_permissao:
        return sem_permissao

    form = UsuarioSistemaForm(
        request.POST or None,
        request_user=request.user,
    )

    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        messages.success(request, "Profissional criado com sucesso.")
        return redirect("seguranca_usuario_editar", usuario_id=usuario.id)

    return render(
        request,
        "accounts/usuario_form.html",
        {
            "form": form,
            "titulo": "Novo profissional",
            "subtitulo": "Cadastre login, dados profissionais, senha e paineis liberados.",
            "usuario_editado": None,
        },
    )


@login_required
def seguranca_usuario_editar(request, usuario_id):
    sem_permissao = redirecionar_sem_permissao(request)
    if sem_permissao:
        return sem_permissao

    usuario = get_object_or_404(Usuario, id=usuario_id)
    form = UsuarioSistemaForm(
        request.POST or None,
        instance=usuario,
        request_user=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profissional atualizado com sucesso.")
        return redirect("seguranca_usuarios")

    return render(
        request,
        "accounts/usuario_form.html",
        {
            "form": form,
            "titulo": "Editar profissional",
            "subtitulo": "Atualize dados profissionais, categoria, paineis e status.",
            "usuario_editado": usuario,
        },
    )


@login_required
@require_POST
def seguranca_usuario_status(request, usuario_id):
    sem_permissao = redirecionar_sem_permissao(request)
    if sem_permissao:
        return sem_permissao

    usuario = get_object_or_404(Usuario, id=usuario_id)

    if usuario.id == request.user.id:
        messages.error(request, "Voce nao pode inativar o proprio acesso.")
        return redirect("seguranca_usuarios")

    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=["is_active"])

    if usuario.is_active:
        messages.success(request, f"Profissional {usuario.username} ativado.")
    else:
        messages.warning(request, f"Profissional {usuario.username} inativado.")

    return redirect("seguranca_usuarios")
