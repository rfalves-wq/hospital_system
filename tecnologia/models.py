import re

from django.conf import settings
from django.db import models


MAC_FORMAT_RE = re.compile(r"^[0-9A-F]{2}(:[0-9A-F]{2}){5}$")


def normalizar_mac(valor):
    texto = (valor or "").strip()

    if not texto:
        return ""

    texto = texto.replace("-", ":").upper()

    if not MAC_FORMAT_RE.fullmatch(texto):
        return ""

    return texto


class EquipamentoTI(models.Model):
    COMPUTADOR = "COMPUTADOR"
    CELULAR = "CELULAR"
    CAMERA = "CAMERA"
    DVR = "DVR"
    IMPRESSORA = "IMPRESSORA"
    SERVIDOR = "SERVIDOR"
    REDE = "REDE"
    OUTRO = "OUTRO"

    TIPO_CHOICES = [
        (COMPUTADOR, "Computador"),
        (CELULAR, "Celular/Tablet"),
        (CAMERA, "Camera"),
        (DVR, "DVR/NVR"),
        (IMPRESSORA, "Impressora"),
        (SERVIDOR, "Servidor"),
        (REDE, "Rede"),
        (OUTRO, "Outro"),
    ]

    IP_DESCONHECIDO = "DESCONHECIDO"
    IP_DHCP = "DHCP"
    IP_FIXO = "FIXO"

    ORIGEM_IP_CHOICES = [
        (IP_DESCONHECIDO, "Nao identificado"),
        (IP_DHCP, "DHCP"),
        (IP_FIXO, "Fixo"),
    ]

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DESCONHECIDO = "DESCONHECIDO"

    STATUS_CHOICES = [
        (ONLINE, "Online"),
        (OFFLINE, "Offline"),
        (DESCONHECIDO, "Nao verificado"),
    ]

    nome = models.CharField(max_length=120)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=COMPUTADOR)
    setor = models.CharField(max_length=120, blank=True, default="")
    endereco_rede = models.CharField(
        "IP ou nome da maquina",
        max_length=180,
        help_text="Ex: 192.168.0.10 ou impressora-recepcao"
    )
    mac_address = models.CharField("MAC", max_length=17, blank=True, default="")
    origem_ip = models.CharField(
        "Origem do IP",
        max_length=20,
        choices=ORIGEM_IP_CHOICES,
        default=IP_DESCONHECIDO
    )
    ativo = models.BooleanField(default=True)
    ultimo_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=DESCONHECIDO
    )
    ultimo_tempo_ms = models.PositiveIntegerField(blank=True, null=True)
    ultima_verificacao = models.DateTimeField(blank=True, null=True)
    observacao = models.TextField(blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Equipamento de TI"
        verbose_name_plural = "Equipamentos de TI"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class ChamadoManutencaoTI(models.Model):
    SUPORTE = "SUPORTE"
    MANUTENCAO = "MANUTENCAO"
    INSTALACAO = "INSTALACAO"
    REDE = "REDE"
    SISTEMA = "SISTEMA"
    OUTRO = "OUTRO"

    TIPO_SERVICO_CHOICES = [
        (SUPORTE, "Suporte"),
        (MANUTENCAO, "Manutencao"),
        (INSTALACAO, "Instalacao"),
        (REDE, "Rede/Internet"),
        (SISTEMA, "Sistema"),
        (OUTRO, "Outro"),
    ]

    BAIXA = "BAIXA"
    NORMAL = "NORMAL"
    ALTA = "ALTA"
    URGENTE = "URGENTE"

    PRIORIDADE_CHOICES = [
        (BAIXA, "Baixa"),
        (NORMAL, "Normal"),
        (ALTA, "Alta"),
        (URGENTE, "Urgente"),
    ]

    ABERTO = "ABERTO"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDO = "CONCLUIDO"
    CANCELADO = "CANCELADO"

    STATUS_CHOICES = [
        (ABERTO, "Aberto"),
        (EM_ANDAMENTO, "Em andamento"),
        (CONCLUIDO, "Concluido"),
        (CANCELADO, "Cancelado"),
    ]
    STATUS_ATIVOS = (ABERTO, EM_ANDAMENTO)

    equipamento = models.ForeignKey(
        EquipamentoTI,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="chamados_manutencao"
    )
    tipo_servico = models.CharField(
        max_length=20,
        choices=TIPO_SERVICO_CHOICES,
        default=SUPORTE
    )
    titulo = models.CharField(max_length=140)
    descricao = models.TextField(blank=True, default="")
    prioridade = models.CharField(
        max_length=20,
        choices=PRIORIDADE_CHOICES,
        default=NORMAL
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=ABERTO
    )
    solicitado_por = models.CharField(max_length=120, blank=True, default="")
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="chamados_ti_solicitados"
    )
    setor_solicitante = models.CharField(max_length=120, blank=True, default="")
    contato = models.CharField(max_length=120, blank=True, default="")
    resposta_ti = models.TextField("Resposta do TI", blank=True, default="")
    respondido_por = models.CharField(max_length=120, blank=True, default="")
    respondido_em = models.DateTimeField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    concluido_em = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Pedido de servico de TI"
        verbose_name_plural = "Pedidos de servico de TI"
        ordering = ["-criado_em"]

    def __str__(self):
        alvo = self.equipamento or self.setor_solicitante or self.solicitado_por or "TI"
        return f"{self.titulo} - {alvo}"
