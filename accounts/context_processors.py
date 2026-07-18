from .permissions import mapa_paineis_usuario, usuario_codigos_paineis
from .utils import (
    conselho_profissional_request,
    identificacao_conselho_request,
    nome_profissional_request,
    registro_profissional_request,
)


def acessos_usuario(request):
    user = getattr(request, "user", None)

    return {
        "paineis_usuario": mapa_paineis_usuario(user),
        "codigos_paineis_usuario": usuario_codigos_paineis(user),
        "profissional_logado": nome_profissional_request(request),
        "profissional_logado_conselho": conselho_profissional_request(request),
        "profissional_logado_registro": registro_profissional_request(request),
        "profissional_logado_conselho_registro": identificacao_conselho_request(request),
    }
