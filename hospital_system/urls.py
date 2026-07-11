from django.contrib import admin
from django.urls import path, include


urlpatterns = [

    path("admin/", admin.site.urls),

    path("", include("accounts.urls")),

    path("dashboard/", include("dashboard.urls")),

    path("acolhimento/", include("acolhimento.urls")),

    path("recepcao/", include("recepcao.urls")),

    path("classificacao/", include("classificacao.urls")),

    path("medico/", include("medico.urls")),
    
    path("laboratorio/", include("laboratorio.urls")),
    
    path("imagem/", include("imagem.urls")),
    
    path("medicacao/", include("medicacao.urls")),
    
    path("farmacia/", include("farmacia.urls")),

    path("internacao/", include("internacao.urls")),
]
