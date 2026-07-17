from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .permissions import painel_por_caminho, usuario_tem_painel


class LoginPermissaoMiddleware:
    caminhos_livres = (
        "",
        "admin/",
        "painel/",
        "favicon.ico",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        caminho = request.path_info.lstrip("/")

        if self.caminho_livre(caminho):
            return self.get_response(request)

        if not request.user.is_authenticated:
            login_url = settings.LOGIN_URL or reverse("login")
            return redirect(f"{login_url}?next={request.get_full_path()}")

        codigo_painel = painel_por_caminho(caminho)

        if codigo_painel and not usuario_tem_painel(request.user, codigo_painel):
            messages.error(
                request,
                "Voce nao tem acesso a esta area. Solicite liberacao ao administrador."
            )
            return redirect("dashboard")

        return self.get_response(request)

    def caminho_livre(self, caminho):
        static_url = (settings.STATIC_URL or "").lstrip("/")

        if static_url and caminho.startswith(static_url):
            return True

        for livre in self.caminhos_livres:
            if not livre:
                if caminho == "":
                    return True
                continue

            if caminho == livre.rstrip("/") or caminho.startswith(livre):
                return True

        return False
