from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from acolhimento.tempos import entrada_setor
from accounts.utils import nome_profissional_request
from medico.models import ConsultaMedica

from .forms import ResultadoImagemForm


SETORES_IMAGEM = {
    "raiox": {
        "nome": "Raio-X",
        "marcador": "RAIO-X",
        "realizado": "raiox_realizado",
        "resultado": "resultado_raiox",
        "data": "data_resultado_raiox",
        "tecnico_nome": "tecnico_raiox_nome",
        "tecnico_registro": "tecnico_raiox_registro",
        "indicacao": "indicacao_raiox",
    },
    "tomografia": {
        "nome": "Tomografia",
        "marcador": "TOMOGRAFIA",
        "realizado": "tomografia_realizada",
        "resultado": "resultado_tomografia",
        "data": "data_resultado_tomografia",
        "tecnico_nome": "tecnico_tomografia_nome",
        "tecnico_registro": "tecnico_tomografia_registro",
        "indicacao": "indicacao_tomografia",
    },
    "mamografia": {
        "nome": "Mamografia",
        "marcador": "MAMOGRAFIA",
        "realizado": "mamografia_realizada",
        "resultado": "resultado_mamografia",
        "data": "data_resultado_mamografia",
        "tecnico_nome": "tecnico_mamografia_nome",
        "tecnico_registro": "tecnico_mamografia_registro",
        "indicacao": "indicacao_outros_imagem",
    },
    "densitometria": {
        "nome": "Densitometria",
        "marcador": "DENSITOMETRIA",
        "realizado": "densitometria_realizada",
        "resultado": "resultado_densitometria",
        "data": "data_resultado_densitometria",
        "tecnico_nome": "tecnico_densitometria_nome",
        "tecnico_registro": "tecnico_densitometria_registro",
        "indicacao": "indicacao_outros_imagem",
    },
}


def setor_foi_solicitado(consulta, setor_key):
    texto = (consulta.exames_imagem or "").upper()
    setor = SETORES_IMAGEM[setor_key]

    if setor_key == "raiox":
        return "RAIO-X" in texto or "RAIO X" in texto

    return setor["marcador"] in texto


def pedido_do_setor(consulta, setor_key):
    texto = consulta.exames_imagem or ""
    linhas = texto.splitlines()

    mapa_titulo = {
        "raiox": "RAIO-X",
        "tomografia": "TOMOGRAFIA",
        "mamografia": "MAMOGRAFIA",
        "densitometria": "DENSITOMETRIA",
    }

    setor_desejado = mapa_titulo.get(setor_key)
    titulo_atual = None
    linhas_setor = []

    for linha in linhas:
        linha_limpa = linha.strip()
        linha_upper = linha_limpa.upper()

        if not linha_limpa:
            continue

        if linha_upper.startswith("---"):
            if "RAIO-X" in linha_upper or "RAIO X" in linha_upper:
                titulo_atual = "RAIO-X"
                continue

            if "TOMOGRAFIA" in linha_upper:
                titulo_atual = "TOMOGRAFIA"
                continue

            if "MAMOGRAFIA" in linha_upper:
                titulo_atual = "MAMOGRAFIA"
                continue

            if "DENSITOMETRIA" in linha_upper:
                titulo_atual = "DENSITOMETRIA"
                continue

        if titulo_atual == setor_desejado:
            linhas_setor.append(linha_limpa)

    if linhas_setor:
        return "\n".join(linhas_setor)

    linhas_fallback = []

    for linha in linhas:
        linha_limpa = linha.strip()
        linha_upper = linha_limpa.upper()

        if not linha_limpa:
            continue

        if setor_key == "raiox":
            if linha_upper.startswith("RAIO-X") or linha_upper.startswith("RAIO X"):
                linhas_fallback.append(linha_limpa)

        elif setor_desejado and linha_upper.startswith(setor_desejado):
            linhas_fallback.append(linha_limpa)

    return "\n".join(linhas_fallback)


def todos_exames_imagem_finalizados(consulta):
    for setor_key, setor in SETORES_IMAGEM.items():
        if setor_foi_solicitado(consulta, setor_key):
            if not getattr(consulta, setor["realizado"]):
                return False

    return True


def procedimentos_finalizados(consulta):
    medicacao_pendente = (
        consulta.solicita_medicacao
        and not consulta.medicacao_realizada
    )

    laboratorio_pendente = (
        consulta.solicita_exames_laboratoriais
        and not consulta.exames_laboratoriais_realizados
    )

    imagem_pendente = (
        consulta.solicita_exames_imagem
        and not todos_exames_imagem_finalizados(consulta)
    )

    return not medicacao_pendente and not laboratorio_pendente and not imagem_pendente


def montar_setores_da_consulta(consulta):
    setores = []

    for chave, config in SETORES_IMAGEM.items():
        if setor_foi_solicitado(consulta, chave):
            setores.append({
                "key": chave,
                "nome": config["nome"],
                "pedido": pedido_do_setor(consulta, chave),
                "indicacao": getattr(consulta, config["indicacao"], "") or "",
                "realizado": getattr(consulta, config["realizado"], False),
                "data": getattr(consulta, config["data"], None),
                "tecnico_nome": getattr(consulta, config["tecnico_nome"], "") or "",
                "tecnico_registro": getattr(consulta, config["tecnico_registro"], "") or "",
            })

    return setores


def imagem_dashboard(request):
    consultas = (
        ConsultaMedica.objects
        .select_related("acolhimento", "acolhimento__paciente")
        .prefetch_related("acolhimento__tempos_setores")
        .filter(solicita_exames_imagem=True)
        .exclude(acolhimento__status__in=["FINALIZADO", "AUSENTE"])
        .order_by("data_consulta")
    )

    exames_pendentes = []
    exames_realizados = []

    for consulta in consultas:
        setores = montar_setores_da_consulta(consulta)

        for setor in setores:
            item = {
                "consulta": consulta,
                "setor": setor,
                "entrada_setor": entrada_setor(
                    consulta.acolhimento,
                    "IMAGEM",
                    fallback=consulta.data_consulta,
                ),
            }

            if setor["realizado"]:
                exames_realizados.append(item)
            else:
                exames_pendentes.append(item)

    return render(
        request,
        "imagem/dashboard.html",
        {
            "exames_pendentes": exames_pendentes,
            "exames_realizados": exames_realizados,
            "total_pendentes": len(exames_pendentes),
            "total_realizados": len(exames_realizados),
        }
    )


def lancar_resultado_imagem(request, consulta_id, setor):
    consulta = get_object_or_404(
        ConsultaMedica.objects.select_related(
            "acolhimento",
            "acolhimento__paciente"
        ),
        id=consulta_id,
        solicita_exames_imagem=True,
    )

    if setor not in SETORES_IMAGEM:
        messages.error(request, "Setor de imagem inválido.")
        return redirect("imagem_dashboard")

    if not setor_foi_solicitado(consulta, setor):
        messages.error(request, "Este setor não foi solicitado para este paciente.")
        return redirect("imagem_dashboard")

    setor_config = SETORES_IMAGEM[setor]
    indicacao_setor = getattr(consulta, setor_config["indicacao"], "") or ""
    pedido_setor = pedido_do_setor(consulta, setor)

    if request.method == "POST":
        form = ResultadoImagemForm(
            request.POST,
            setor=setor,
            instance=consulta
        )

        if form.is_valid():
            consulta = form.save(commit=False)

            setattr(consulta, setor_config["realizado"], True)
            setattr(consulta, setor_config["data"], timezone.now())

            if todos_exames_imagem_finalizados(consulta):
                consulta.exames_imagem_realizados = True
                consulta.data_resultado_imagem = timezone.now()
            else:
                consulta.exames_imagem_realizados = False
                consulta.data_resultado_imagem = None

            consulta.save()

            acolhimento = consulta.acolhimento

            if procedimentos_finalizados(consulta):
                acolhimento.status = "RETORNO_MEDICO"
            else:
                acolhimento.status = "PROCEDIMENTOS"

            acolhimento.save()

            messages.success(
                request,
                f"Resultado de {setor_config['nome']} salvo com sucesso."
            )

            return redirect("imagem_dashboard")
    else:
        initial = {}
        campo_tecnico_nome = setor_config["tecnico_nome"]

        if not getattr(consulta, campo_tecnico_nome):
            initial[campo_tecnico_nome] = nome_profissional_request(request)

        form = ResultadoImagemForm(
            setor=setor,
            instance=consulta,
            initial=initial
        )

    return render(
        request,
        "imagem/lancar_resultado.html",
        {
            "form": form,
            "consulta": consulta,
            "acolhimento": consulta.acolhimento,
            "setor": setor,
            "setor_nome": setor_config["nome"],
            "setor_config": setor_config,
            "pedido_setor": pedido_setor,
            "indicacao_setor": indicacao_setor,
        }
    )
