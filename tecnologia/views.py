import json
import os
import ipaddress
import re
import socket
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import EquipamentoTIForm, RedeScanForm
from .models import EquipamentoTI, normalizar_mac


ALVO_REDE_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,180}$")
IPV4_RE = re.compile(
    r"(?<![\d.])"
    r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
    r"(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}"
    r"(?![\d.])"
)
MAC_CAPTURE_RE = re.compile(
    r"\b([0-9a-fA-F]{2}(?:[:-][0-9a-fA-F]{2}){5})\b"
)
HOSTNAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,119}$")
MAX_HOSTS_RASTREIO = 254
SESSION_RASTREIO_KEY = "tecnologia_ultimo_rastreio"
TIPO_LABELS = dict(EquipamentoTI.TIPO_CHOICES)
TIPOS_VALIDOS = {tipo for tipo, _ in EquipamentoTI.TIPO_CHOICES}
ORIGEM_IP_LABELS = dict(EquipamentoTI.ORIGEM_IP_CHOICES)
ABAS_EQUIPAMENTOS_TIPO = (
    ("todos", "Todos", None),
    ("computadores", "Computadores", EquipamentoTI.COMPUTADOR),
    ("cameras", "Cameras", EquipamentoTI.CAMERA),
    ("dvr", "DVR/NVR", EquipamentoTI.DVR),
    ("impressoras", "Impressoras", EquipamentoTI.IMPRESSORA),
    ("celulares", "Celulares/Tablets", EquipamentoTI.CELULAR),
    ("servidores", "Servidores", EquipamentoTI.SERVIDOR),
    ("rede", "Rede", EquipamentoTI.REDE),
    ("outros", "Outros", EquipamentoTI.OUTRO),
)
ABAS_EQUIPAMENTOS_VALIDAS = {chave for chave, _, _ in ABAS_EQUIPAMENTOS_TIPO}

TIPO_HINTS = (
    (
        EquipamentoTI.CELULAR,
        (
            "android",
            "iphone",
            "ipad",
            "galaxy",
            "redmi",
            "xiaomi",
            "moto",
            "motorola",
            "samsung",
            "huawei",
            "honor",
            "realme",
            "oppo",
            "tablet",
            "phone",
            "celular",
        ),
    ),
    (
        EquipamentoTI.DVR,
        (
            "dvr",
            "nvr",
            "gravador",
            "cftv-nvr",
            "cftv-dvr",
        ),
    ),
    (
        EquipamentoTI.CAMERA,
        (
            "camera",
            "ipcam",
            "cam-",
            "cam_",
            "cam.",
            "cftv",
            "hikvision",
            "dahua",
            "intelbras",
            "axis",
            "vivotek",
            "giga",
            "jfl",
        ),
    ),
    (
        EquipamentoTI.IMPRESSORA,
        (
            "printer",
            "print",
            "impressora",
            "hp",
            "epson",
            "brother",
            "canon",
            "xerox",
            "ricoh",
            "lexmark",
        ),
    ),
    (
        EquipamentoTI.SERVIDOR,
        (
            "server",
            "servidor",
            "srv",
            "ad",
            "dc",
            "nas",
            "storage",
        ),
    ),
    (
        EquipamentoTI.REDE,
        (
            "router",
            "roteador",
            "switch",
            "gateway",
            "mikrotik",
            "routerboard",
            "unifi",
            "ubiquiti",
            "omada",
            "tplink",
            "tp-link",
            "ap-",
        ),
    ),
    (
        EquipamentoTI.COMPUTADOR,
        (
            "desktop",
            "notebook",
            "laptop",
            "pc",
            "win",
            "windows",
            "recepcao",
            "farmacia",
        ),
    ),
)


def comando_ping(alvo, timeout_ms=1000):
    if os.name == "nt":
        return ["ping", "-n", "1", "-w", str(timeout_ms), alvo]

    return ["ping", "-c", "1", "-W", "1", alvo]


def executar_ping(alvo):
    inicio = time.perf_counter()

    try:
        resultado = subprocess.run(
            comando_ping(alvo),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=3,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        online = resultado.returncode == 0
        saida = resultado.stdout or ""
    except (OSError, subprocess.TimeoutExpired):
        online = False
        saida = ""

    return online, int((time.perf_counter() - inicio) * 1000), saida


def resolver_ip_alvo(alvo, saida_ping=""):
    alvo = (alvo or "").strip()

    try:
        ip = ipaddress.ip_address(alvo)
    except ValueError:
        ip = None

    if ip and ip.version == 4:
        return str(ip)

    for candidato in IPV4_RE.findall(saida_ping or ""):
        try:
            ip = ipaddress.ip_address(candidato)
        except ValueError:
            continue

        if ip.version == 4:
            return str(ip)

    try:
        return socket.gethostbyname(alvo)
    except OSError:
        return ""


def normalizar_nome_host(valor, ip_texto=""):
    nome = (valor or "").strip().strip(".")

    if not nome or nome == ip_texto or IPV4_RE.fullmatch(nome):
        return ""

    nome = nome[:120]

    if not HOSTNAME_RE.fullmatch(nome):
        return ""

    return nome


def nome_por_saida_ping(saida, ip_texto):
    marcador = f"[{ip_texto}]"

    for linha in (saida or "").splitlines():
        if marcador not in linha:
            continue

        prefixo = linha.split(marcador, 1)[0].strip()
        partes = prefixo.split(maxsplit=1)

        if len(partes) != 2:
            continue

        nome = normalizar_nome_host(partes[1], ip_texto)

        if nome:
            return nome

    return ""


def nome_por_ping_reverso(ip_texto):
    if os.name != "nt":
        return ""

    try:
        resultado = subprocess.run(
            ["ping", "-a", "-n", "1", "-w", "1000", ip_texto],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=3,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""

    return nome_por_saida_ping(resultado.stdout, ip_texto)


def nome_por_nbtstat(ip_texto):
    if os.name != "nt":
        return ""

    try:
        resultado = subprocess.run(
            ["nbtstat", "-A", ip_texto],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=3,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""

    linhas = resultado.stdout.splitlines()

    for etiqueta in ("<00>", "<20>"):
        for linha in linhas:
            linha_upper = linha.upper()

            if etiqueta not in linha_upper:
                continue

            if "GROUP" in linha_upper or "GRUPO" in linha_upper:
                continue

            partes = linha.split()

            if not partes:
                continue

            nome = normalizar_nome_host(partes[0], ip_texto)

            if nome:
                return nome

    return ""


def nome_por_dns_reverso(ip_texto):
    try:
        nome = socket.gethostbyaddr(ip_texto)[0]
    except OSError:
        return ""

    return normalizar_nome_host(nome, ip_texto)


def nome_por_ip(ip_texto, saida_ping=""):
    ip_texto = (ip_texto or "").strip()

    try:
        ip = ipaddress.ip_address(ip_texto)
    except ValueError:
        return ""

    if ip.version != 4:
        return ""

    for descoberta in (
        lambda: nome_por_saida_ping(saida_ping, ip_texto),
        lambda: nome_por_ping_reverso(ip_texto),
        lambda: nome_por_nbtstat(ip_texto),
        lambda: nome_por_dns_reverso(ip_texto),
    ):
        nome = descoberta()

        if nome:
            return nome

    return ""


def inferir_tipo_equipamento(nome_host="", mac="", ip_texto=""):
    texto = f"{nome_host or ''} {mac or ''} {ip_texto or ''}".lower()

    for tipo, pistas in TIPO_HINTS:
        if any(pista in texto for pista in pistas):
            return tipo

    return EquipamentoTI.OUTRO


def normalizar_tipo(valor):
    tipo = (valor or "").strip().upper()

    if tipo in TIPOS_VALIDOS:
        return tipo

    return EquipamentoTI.OUTRO


def rotulo_tipo(tipo):
    return TIPO_LABELS.get(tipo, TIPO_LABELS[EquipamentoTI.OUTRO])


def rotulo_origem_ip(origem_ip):
    return ORIGEM_IP_LABELS.get(
        origem_ip,
        ORIGEM_IP_LABELS[EquipamentoTI.IP_DESCONHECIDO]
    )


def extrair_mac_arp(saida, ip_texto):
    for linha in (saida or "").splitlines():
        if ip_texto not in linha:
            continue

        encontrado = MAC_CAPTURE_RE.search(linha)

        if encontrado:
            return normalizar_mac(encontrado.group(1))

    return ""


def mac_por_ip(ip_texto):
    ip_texto = (ip_texto or "").strip()

    try:
        ip = ipaddress.ip_address(ip_texto)
    except ValueError:
        return ""

    if ip.version != 4:
        return ""

    comandos = (
        ["arp", "-a", ip_texto],
        ["arp", "-a"],
    )

    for comando in comandos:
        try:
            resultado = subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=2,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
        except (OSError, subprocess.TimeoutExpired):
            continue

        mac = extrair_mac_arp(resultado.stdout, ip_texto)

        if mac:
            return mac

    return ""


def verificar_equipamento(equipamento):
    alvo = (equipamento.endereco_rede or "").strip()

    if not ALVO_REDE_RE.fullmatch(alvo):
        equipamento.ultimo_status = EquipamentoTI.OFFLINE
        equipamento.ultimo_tempo_ms = None
        equipamento.ultima_verificacao = timezone.now()
        equipamento.save(
            update_fields=[
                "ultimo_status",
                "ultimo_tempo_ms",
                "ultima_verificacao",
                "atualizado_em",
            ]
        )
        return equipamento

    online, tempo_ms, saida_ping = executar_ping(alvo)
    mac = ""
    nome_host = ""

    if online:
        ip_resolvido = resolver_ip_alvo(alvo, saida_ping)
        mac = mac_por_ip(ip_resolvido)
        nome_host = nome_por_ip(ip_resolvido, saida_ping)
        tipo_sugerido = inferir_tipo_equipamento(nome_host, mac, ip_resolvido)

    equipamento.ultimo_status = (
        EquipamentoTI.ONLINE if online else EquipamentoTI.OFFLINE
    )
    equipamento.ultimo_tempo_ms = tempo_ms
    equipamento.ultima_verificacao = timezone.now()
    update_fields = [
        "ultimo_status",
        "ultimo_tempo_ms",
        "ultima_verificacao",
        "atualizado_em",
    ]

    if mac:
        equipamento.mac_address = mac
        update_fields.append("mac_address")

    nomes_genericos = {
        f"Equipamento {alvo}",
        f"Equipamento {resolver_ip_alvo(alvo, saida_ping)}",
    }

    if nome_host and equipamento.nome in nomes_genericos:
        equipamento.nome = nome_host
        update_fields.append("nome")

    if online and equipamento.tipo == EquipamentoTI.OUTRO and tipo_sugerido:
        equipamento.tipo = tipo_sugerido
        update_fields.append("tipo")

    equipamento.save(
        update_fields=update_fields
    )

    return equipamento


def verificar_lista_equipamentos(equipamentos):
    total = 0

    for equipamento in equipamentos:
        verificar_equipamento(equipamento)
        total += 1

    return total


def ping_alvo(alvo):
    online, tempo_ms, saida_ping = executar_ping(alvo)
    mac = ""
    nome_host = ""

    if online:
        ip_resolvido = resolver_ip_alvo(alvo, saida_ping)
        mac = mac_por_ip(ip_resolvido)
        nome_host = nome_por_ip(ip_resolvido, saida_ping)
        tipo_sugerido = inferir_tipo_equipamento(nome_host, mac, ip_resolvido)
    else:
        tipo_sugerido = EquipamentoTI.OUTRO

    return {
        "ip": alvo,
        "online": online,
        "tempo_ms": tempo_ms,
        "mac": mac,
        "nome_host": nome_host,
        "tipo_sugerido": tipo_sugerido,
        "tipo_sugerido_label": rotulo_tipo(tipo_sugerido),
        "origem_ip": EquipamentoTI.IP_DESCONHECIDO,
        "origem_ip_label": rotulo_origem_ip(EquipamentoTI.IP_DESCONHECIDO),
    }


def normalizar_rede(cidr):
    entrada = (cidr or "").strip()

    if "/" not in entrada:
        try:
            ip = ipaddress.ip_address(entrada)
        except ValueError as exc:
            raise ValueError(
                "Informe uma faixa valida ou um IP. Ex: 192.168.3.0/24 ou 192.168.3.25."
            ) from exc

        if ip.version != 4:
            raise ValueError("Use IPv4. Ex: 192.168.3.0/24.")

        return ipaddress.ip_network(f"{ip}/24", strict=False)

    try:
        rede = ipaddress.ip_network(entrada, strict=False)
    except ValueError as exc:
        raise ValueError("Informe uma faixa valida. Ex: 192.168.3.0/24.") from exc

    if rede.version != 4:
        raise ValueError("Use uma faixa IPv4. Ex: 192.168.3.0/24.")

    return rede


def rastrear_rede(cidr):
    rede = normalizar_rede(cidr)

    hosts = [str(host) for host in rede.hosts()]

    if not hosts and rede.num_addresses == 1:
        hosts = [str(rede.network_address)]

    if len(hosts) > MAX_HOSTS_RASTREIO:
        raise ValueError(
            f"Faixa muito grande. Use no maximo {MAX_HOSTS_RASTREIO} enderecos por rastreio."
        )

    resultados = []
    max_workers = min(8, max(1, len(hosts)))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        tarefas = {
            executor.submit(ping_alvo, host): host
            for host in hosts
        }

        for tarefa in as_completed(tarefas):
            resultados.append(tarefa.result())

    return (
        sorted(
            [item for item in resultados if item["online"]],
            key=lambda item: ipaddress.ip_address(item["ip"])
        ),
        str(rede),
    )


def redes_locais_sugeridas():
    redes = set()

    try:
        infos = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
    except OSError:
        infos = []

    for info in infos:
        ip_texto = info[4][0]

        try:
            ip = ipaddress.ip_address(ip_texto)
        except ValueError:
            continue

        if ip.is_loopback or ip.is_link_local or not ip.is_private:
            continue

        redes.add(str(ipaddress.ip_network(f"{ip}/24", strict=False)))

    return sorted(redes, key=lambda rede: ipaddress.ip_network(rede).network_address)


def atualizar_cadastrados_rastreio(resultados):
    ips_cadastrados = set(
        EquipamentoTI.objects.values_list("endereco_rede", flat=True)
    )

    for item in resultados:
        item["cadastrado"] = item.get("ip") in ips_cadastrados
        tipo_sugerido = normalizar_tipo(
            item.get("tipo_sugerido")
            or inferir_tipo_equipamento(
                item.get("nome_host"),
                item.get("mac"),
                item.get("ip"),
            )
        )
        item["tipo_sugerido"] = tipo_sugerido
        item["tipo_sugerido_label"] = rotulo_tipo(tipo_sugerido)
        item["origem_ip"] = item.get("origem_ip") or EquipamentoTI.IP_DESCONHECIDO
        item["origem_ip_label"] = rotulo_origem_ip(item["origem_ip"])

    return resultados


def resumo_do_rastreio(rede, resultados, mantido=False):
    novos = sum(1 for item in resultados if not item.get("cadastrado"))

    return {
        "rede": rede,
        "online": len(resultados),
        "novos": novos,
        "mantido": mantido,
    }


def salvar_rastreio_sessao(request, rede, resultados):
    request.session[SESSION_RASTREIO_KEY] = {
        "rede": rede,
        "resultados": resultados,
    }
    request.session.modified = True


def carregar_rastreio_sessao(request):
    dados = request.session.get(SESSION_RASTREIO_KEY)

    if not dados:
        return None, None

    resultados = dados.get("resultados") or []
    rede = dados.get("rede") or ""
    atualizar_cadastrados_rastreio(resultados)
    salvar_rastreio_sessao(request, rede, resultados)

    return resultados, resumo_do_rastreio(rede, resultados, mantido=True)


def manter_rastreio_redirect(request):
    if request.session.get(SESSION_RASTREIO_KEY):
        return redirect(f"{reverse('tecnologia_dashboard')}?ultimo_rastreio=1")

    return redirect("tecnologia_dashboard")


def redirect_dashboard_aba(request):
    aba = request.POST.get("aba") or request.GET.get("aba")

    if aba in ABAS_EQUIPAMENTOS_VALIDAS and aba != "todos":
        return redirect(f"{reverse('tecnologia_dashboard')}?aba={aba}")

    return redirect("tecnologia_dashboard")


def criar_equipamento_descoberto(
    ip_encontrado,
    mac_encontrado="",
    nome_encontrado="",
    tipo_sugerido="",
):
    return EquipamentoTI.objects.create(
        nome=nome_encontrado or f"Equipamento {ip_encontrado}",
        tipo=normalizar_tipo(tipo_sugerido),
        endereco_rede=ip_encontrado,
        mac_address=mac_encontrado,
        origem_ip=EquipamentoTI.IP_DESCONHECIDO,
        ultimo_status=EquipamentoTI.ONLINE,
        ultima_verificacao=timezone.now(),
    )


def texto_ultima_verificacao(equipamento):
    if not equipamento.ultima_verificacao:
        return "Ainda nao verificado"

    ultima = equipamento.ultima_verificacao

    if timezone.is_aware(ultima):
        ultima = timezone.localtime(ultima)

    texto = ultima.strftime("%d/%m/%Y %H:%M")

    if equipamento.ultimo_tempo_ms is not None:
        texto = f"{texto} - {equipamento.ultimo_tempo_ms} ms"

    return texto


def payload_equipamento_status(equipamento):
    return {
        "id": equipamento.id,
        "nome": equipamento.nome,
        "status": equipamento.ultimo_status,
        "status_class": equipamento.ultimo_status.lower(),
        "status_label": equipamento.get_ultimo_status_display(),
        "tempo_ms": equipamento.ultimo_tempo_ms,
        "ultima_verificacao": texto_ultima_verificacao(equipamento),
        "mac_address": equipamento.mac_address,
    }


def totais_status_payload():
    equipamentos = EquipamentoTI.objects.all()

    return {
        "total": equipamentos.count(),
        "online": equipamentos.filter(ultimo_status=EquipamentoTI.ONLINE).count(),
        "offline": equipamentos.filter(ultimo_status=EquipamentoTI.OFFLINE).count(),
        "desconhecidos": equipamentos.filter(
            ultimo_status=EquipamentoTI.DESCONHECIDO
        ).count(),
    }


@login_required
@require_POST
def tecnologia_status(request):
    try:
        dados = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        dados = {}

    ids = dados.get("ids") or []
    ids_validos = []

    for item in ids:
        try:
            ids_validos.append(int(item))
        except (TypeError, ValueError):
            continue

    equipamentos = EquipamentoTI.objects.filter(ativo=True)

    if ids_validos:
        equipamentos = equipamentos.filter(id__in=ids_validos)

    atualizados = []

    for equipamento in equipamentos:
        verificar_equipamento(equipamento)
        atualizados.append(payload_equipamento_status(equipamento))

    return JsonResponse(
        {
            "equipamentos": atualizados,
            "totais": totais_status_payload(),
        }
    )


@login_required
def tecnologia_dashboard(request):
    equipamento_edicao = None
    resultados_rastreio = None
    resumo_rastreio = None

    if request.method == "POST":
        acao = request.POST.get("acao")
        scan_form = RedeScanForm()

        if acao == "cadastrar":
            form = EquipamentoTIForm(request.POST)

            if form.is_valid():
                equipamento = form.save()
                verificar_equipamento(equipamento)
                messages.success(request, "Equipamento cadastrado com sucesso.")
                return redirect("tecnologia_dashboard")
        elif acao == "atualizar":
            equipamento_edicao = get_object_or_404(
                EquipamentoTI,
                id=request.POST.get("equipamento_id")
            )
            form = EquipamentoTIForm(request.POST, instance=equipamento_edicao)

            if form.is_valid():
                equipamento = form.save()
                verificar_equipamento(equipamento)
                messages.success(request, "Equipamento atualizado com sucesso.")
                return redirect_dashboard_aba(request)
        elif acao == "cadastrar_descoberto":
            ip_encontrado = (request.POST.get("ip") or "").strip()
            mac_encontrado = normalizar_mac(request.POST.get("mac"))
            nome_encontrado = normalizar_nome_host(
                request.POST.get("nome_host"),
                ip_encontrado
            )
            tipo_sugerido = normalizar_tipo(request.POST.get("tipo_sugerido"))

            if not ip_encontrado:
                messages.error(request, "IP descoberto invalido.")
                return manter_rastreio_redirect(request)

            equipamento = EquipamentoTI.objects.filter(
                endereco_rede=ip_encontrado
            ).first()

            if equipamento:
                update_fields = []

                if mac_encontrado and equipamento.mac_address != mac_encontrado:
                    equipamento.mac_address = mac_encontrado
                    update_fields.append("mac_address")

                nomes_genericos = {
                    f"Equipamento {ip_encontrado}",
                    equipamento.endereco_rede,
                }

                if nome_encontrado and equipamento.nome in nomes_genericos:
                    equipamento.nome = nome_encontrado
                    update_fields.append("nome")

                if (
                    tipo_sugerido != EquipamentoTI.OUTRO
                    and equipamento.tipo == EquipamentoTI.OUTRO
                ):
                    equipamento.tipo = tipo_sugerido
                    update_fields.append("tipo")

                if update_fields:
                    update_fields.append("atualizado_em")
                    equipamento.save(update_fields=update_fields)

                messages.info(
                    request,
                    f"O IP {ip_encontrado} ja estava cadastrado como {equipamento.nome}."
                )
            else:
                criar_equipamento_descoberto(
                    ip_encontrado,
                    mac_encontrado,
                    nome_encontrado,
                    tipo_sugerido
                )
                messages.success(
                    request,
                    f"Equipamento {nome_encontrado or ip_encontrado} cadastrado. Edite o setor quando quiser."
                )

            return manter_rastreio_redirect(request)
        elif acao == "cadastrar_todos_descobertos":
            resultados_salvos, _ = carregar_rastreio_sessao(request)

            if not resultados_salvos:
                messages.warning(request, "Nenhum rastreio salvo para cadastrar.")
                return redirect("tecnologia_dashboard")

            cadastrados = 0
            existentes = 0

            for item in resultados_salvos:
                ip_encontrado = (item.get("ip") or "").strip()

                if not ip_encontrado:
                    continue

                mac_encontrado = normalizar_mac(item.get("mac"))
                nome_encontrado = normalizar_nome_host(
                    item.get("nome_host"),
                    ip_encontrado
                )
                tipo_sugerido = normalizar_tipo(item.get("tipo_sugerido"))
                equipamento = EquipamentoTI.objects.filter(
                    endereco_rede=ip_encontrado
                ).first()

                if equipamento:
                    existentes += 1
                    continue

                criar_equipamento_descoberto(
                    ip_encontrado,
                    mac_encontrado,
                    nome_encontrado,
                    tipo_sugerido
                )
                cadastrados += 1

            if cadastrados:
                messages.success(
                    request,
                    f"{cadastrados} equipamento(s) cadastrado(s) sem novo rastreio."
                )
            else:
                messages.info(
                    request,
                    f"Nenhum equipamento novo para cadastrar. {existentes} ja constavam no sistema."
                )

            return manter_rastreio_redirect(request)
        elif acao == "limpar_rastreio":
            request.session.pop(SESSION_RASTREIO_KEY, None)
            request.session.modified = True
            messages.info(request, "Lista do ultimo rastreio limpa.")
            return redirect("tecnologia_dashboard")
        elif acao == "excluir":
            equipamento = get_object_or_404(
                EquipamentoTI,
                id=request.POST.get("equipamento_id")
            )
            nome = equipamento.nome
            equipamento.delete()
            messages.success(request, f"Equipamento {nome} excluido.")
            return redirect_dashboard_aba(request)
        elif acao == "verificar_todos":
            total = verificar_lista_equipamentos(
                EquipamentoTI.objects.filter(ativo=True)
            )
            messages.success(
                request,
                f"Verificacao concluida para {total} equipamento(s)."
            )
            return redirect("tecnologia_dashboard")
        elif acao == "verificar_um":
            equipamento = get_object_or_404(
                EquipamentoTI,
                id=request.POST.get("equipamento_id")
            )
            verificar_equipamento(equipamento)
            messages.success(
                request,
                f"Status atualizado: {equipamento.nome}."
            )
            return redirect_dashboard_aba(request)
        elif acao == "rastrear_rede":
            form = EquipamentoTIForm()
            scan_form = RedeScanForm(request.POST)

            if scan_form.is_valid():
                rede = scan_form.cleaned_data["rede"]

                try:
                    resultados_rastreio, rede_normalizada = rastrear_rede(rede)
                    atualizar_cadastrados_rastreio(resultados_rastreio)
                    resumo_rastreio = resumo_do_rastreio(
                        rede_normalizada,
                        resultados_rastreio
                    )
                    salvar_rastreio_sessao(
                        request,
                        rede_normalizada,
                        resultados_rastreio
                    )
                except ValueError as exc:
                    scan_form.add_error("rede", str(exc))
        else:
            form = EquipamentoTIForm()
    else:
        scan_form = RedeScanForm()
        editar_id = request.GET.get("editar")

        if editar_id:
            equipamento_edicao = get_object_or_404(EquipamentoTI, id=editar_id)
            form = EquipamentoTIForm(instance=equipamento_edicao)
        else:
            form = EquipamentoTIForm()

        if request.GET.get("ultimo_rastreio"):
            resultados_rastreio, resumo_rastreio = carregar_rastreio_sessao(request)

    equipamentos_base = EquipamentoTI.objects.all()
    online = equipamentos_base.filter(ultimo_status=EquipamentoTI.ONLINE).count()
    offline = equipamentos_base.filter(ultimo_status=EquipamentoTI.OFFLINE).count()
    desconhecidos = equipamentos_base.filter(
        ultimo_status=EquipamentoTI.DESCONHECIDO
    ).count()
    total_equipamentos = equipamentos_base.count()
    aba_equipamentos = request.GET.get("aba", "todos")

    if aba_equipamentos not in ABAS_EQUIPAMENTOS_VALIDAS:
        aba_equipamentos = "todos"

    equipamentos = equipamentos_base
    tipo_por_aba = {
        chave: tipo
        for chave, _, tipo in ABAS_EQUIPAMENTOS_TIPO
        if tipo
    }
    tipo_filtrado = tipo_por_aba.get(aba_equipamentos)

    if tipo_filtrado:
        equipamentos = equipamentos.filter(tipo=tipo_filtrado)

    abas_equipamentos = []

    for chave, label, tipo in ABAS_EQUIPAMENTOS_TIPO:
        total_aba = (
            total_equipamentos
            if tipo is None
            else equipamentos_base.filter(tipo=tipo).count()
        )
        abas_equipamentos.append(
            {
                "chave": chave,
                "label": label,
                "total": total_aba,
                "ativa": aba_equipamentos == chave,
            }
        )

    return render(
        request,
        "tecnologia/dashboard.html",
        {
            "form": form,
            "scan_form": scan_form,
            "equipamento_edicao": equipamento_edicao,
            "equipamentos": equipamentos,
            "aba_equipamentos": aba_equipamentos,
            "abas_equipamentos": abas_equipamentos,
            "resultados_rastreio": resultados_rastreio,
            "resumo_rastreio": resumo_rastreio,
            "redes_sugeridas": redes_locais_sugeridas(),
            "total_equipamentos": total_equipamentos,
            "total_online": online,
            "total_offline": offline,
            "total_desconhecidos": desconhecidos,
        }
    )
