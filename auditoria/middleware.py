from .models import EventoAuditoria
from .services import registrar_evento


class AuditoriaMiddleware:
    METODOS_GRAVACAO = {"POST", "PUT", "PATCH", "DELETE"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        usuario_antes = (
            request.user
            if getattr(request, "user", None) and request.user.is_authenticated
            else None
        )
        response = self.get_response(request)

        try:
            self.registrar(request, response, usuario_antes)
        except Exception:
            pass

        return response

    def registrar(self, request, response, usuario_antes):
        acao = self.acao_request(request, response)
        if not acao:
            return

        usuario = (
            request.user
            if getattr(request, "user", None) and request.user.is_authenticated
            else usuario_antes
        )

        if not usuario and acao != EventoAuditoria.FALHA_LOGIN:
            return

        registrar_evento(
            request=request,
            acao=acao,
            descricao=self.descricao_evento(acao, response),
            usuario=usuario,
            status_code=getattr(response, "status_code", None),
        )

    def acao_request(self, request, response):
        metodo = (request.method or "").upper()
        caminho = (request.path_info or "").lower()
        status_code = getattr(response, "status_code", 0) or 0

        if caminho.startswith("/static/") or caminho.startswith("/admin/"):
            return ""

        if caminho in ("", "/") and metodo == "POST":
            if status_code in (301, 302, 303, 307, 308):
                return EventoAuditoria.LOGIN
            return EventoAuditoria.FALHA_LOGIN

        if caminho.startswith("/sair"):
            return EventoAuditoria.LOGOUT

        if status_code == 403:
            return EventoAuditoria.ACESSO_NEGADO

        if status_code >= 500:
            return EventoAuditoria.ERRO

        if "imprimir" in caminho or "reimprimir" in caminho:
            return EventoAuditoria.IMPRESSAO

        if metodo not in self.METODOS_GRAVACAO:
            return ""

        if "reenviar" in caminho or "enviar" in caminho:
            return EventoAuditoria.REENVIO

        if "assumir" in caminho:
            return EventoAuditoria.ASSUMIR

        if "status" in caminho or request.POST.get("status"):
            return EventoAuditoria.STATUS

        return EventoAuditoria.GRAVACAO

    def descricao_evento(self, acao, response):
        descricao = {
            EventoAuditoria.LOGIN: "Login realizado no sistema.",
            EventoAuditoria.FALHA_LOGIN: "Tentativa de login sem sucesso.",
            EventoAuditoria.LOGOUT: "Sessao encerrada.",
            EventoAuditoria.GRAVACAO: "Dados gravados ou alterados.",
            EventoAuditoria.STATUS: "Status alterado.",
            EventoAuditoria.IMPRESSAO: "Documento enviado para impressao.",
            EventoAuditoria.REENVIO: "Registro reenviado.",
            EventoAuditoria.ASSUMIR: "Profissional assumiu atendimento.",
            EventoAuditoria.ACESSO_NEGADO: "Acesso negado pelo sistema.",
            EventoAuditoria.ERRO: "Erro interno registrado na requisicao.",
        }.get(acao, "Acao registrada.")

        status_code = getattr(response, "status_code", None)
        if status_code:
            return f"{descricao} HTTP {status_code}."

        return descricao
