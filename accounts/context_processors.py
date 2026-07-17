from .permissions import mapa_paineis_usuario, usuario_codigos_paineis


def acessos_usuario(request):
    user = getattr(request, "user", None)

    return {
        "paineis_usuario": mapa_paineis_usuario(user),
        "codigos_paineis_usuario": usuario_codigos_paineis(user),
    }
