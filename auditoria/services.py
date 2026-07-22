import re

from django.db import DatabaseError, OperationalError

from accounts.permissions import PAINEIS_PADRAO, painel_por_caminho
from accounts.utils import (
    conselho_profissional_usuario,
    nome_profissional_usuario,
    registro_profissional_usuario,
)

from .models import EventoAuditoria


CAMPOS_SENSIVEIS = (
    "csrf",
    "password",
    "senha",
    "token",
    "secret",
)

MODULOS_POR_CODIGO = {
    painel["codigo"]: painel["nome"]
    for painel in PAINEIS_PADRAO
}
MODULOS_POR_CODIGO.update(
    {
        "": "Sistema",
        "auditoria": "Auditoria do Sistema",
        "login": "Login",
    }
)


def valor_curto(valor, limite=180):
    if valor is None:
        return ""

    valor = str(valor)
    if len(valor) <= limite:
        return valor

    return f"{valor[:limite]}..."


def limpar_dados_querydict(querydict):
    dados = {}

    for chave in querydict:
        chave_limpa = str(chave)
        chave_baixa = chave_limpa.lower()

        if any(sensivel in chave_baixa for sensivel in CAMPOS_SENSIVEIS):
            continue

        valores = [valor_curto(valor) for valor in querydict.getlist(chave)]
        if not valores:
            continue

        dados[chave_limpa] = valores[0] if len(valores) == 1 else valores

    return dados


def dados_request(request):
    dados = {}

    get_data = limpar_dados_querydict(request.GET)
    post_data = limpar_dados_querydict(request.POST)

    if get_data:
        dados["get"] = get_data

    if post_data:
        dados["post"] = post_data

    return dados


def ip_request(request):
    encaminhado = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if encaminhado:
        return encaminhado.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR") or None


def modulo_request(request):
    caminho = (request.path_info or "").lstrip("/")

    if not caminho:
        return "Login"

    codigo = painel_por_caminho(caminho)
    if codigo:
        return MODULOS_POR_CODIGO.get(codigo, codigo)

    primeira_parte = caminho.split("/", 1)[0]
    if primeira_parte == "auditoria":
        return "Auditoria do Sistema"

    return primeira_parte.replace("-", " ").title() or "Sistema"


def campo_request(request, nomes):
    for nome in nomes:
        valor = request.POST.get(nome) or request.GET.get(nome)
        if valor:
            return valor_curto(valor, 200)

    return ""


def objeto_request(request):
    caminho = request.path_info or ""
    encontrado = re.search(r"/(\d+)(?:/|$)", caminho)

    objeto_id = encontrado.group(1) if encontrado else ""
    objeto_tipo = ""

    if objeto_id:
        partes = [parte for parte in caminho.strip("/").split("/") if parte]
        objeto_tipo = partes[0] if partes else ""

    return objeto_tipo, objeto_id


def usuario_valido(usuario):
    return usuario if usuario and getattr(usuario, "is_authenticated", False) else None


def registrar_evento(
    request,
    acao,
    descricao="",
    modulo="",
    usuario=None,
    status_code=None,
    dados_extra=None,
    usuario_login="",
):
    usuario = usuario_valido(usuario) or usuario_valido(getattr(request, "user", None))
    objeto_tipo, objeto_id = objeto_request(request)
    dados = dados_request(request)

    if dados_extra:
        dados["extra"] = dados_extra

    login_informado = usuario_login or campo_request(request, ["username", "usuario", "login"])

    try:
        EventoAuditoria.objects.create(
            usuario=usuario,
            usuario_login=(getattr(usuario, "username", "") or login_informado or "")[:150],
            profissional=nome_profissional_usuario(usuario)[:180],
            conselho=conselho_profissional_usuario(usuario)[:20],
            registro=registro_profissional_usuario(usuario)[:60],
            acao=acao,
            modulo=(modulo or modulo_request(request))[:80],
            descricao=descricao[:255],
            caminho=(request.get_full_path() or "")[:255],
            metodo=(request.method or "")[:10],
            status_code=status_code,
            ip=ip_request(request),
            navegador=(request.META.get("HTTP_USER_AGENT", "") or "")[:1200],
            objeto_tipo=objeto_tipo[:80],
            objeto_id=objeto_id[:40],
            numero_bam=campo_request(request, ["numero_bam", "bam", "BAM"])[:30],
            nome_paciente=campo_request(request, ["nome_paciente", "paciente"])[:200],
            dados=dados,
        )
    except (DatabaseError, OperationalError):
        return None

    return True
