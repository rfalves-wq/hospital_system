from django.conf import settings
from django.db import models


class EventoAuditoria(models.Model):
    LOGIN = "LOGIN"
    FALHA_LOGIN = "FALHA_LOGIN"
    LOGOUT = "LOGOUT"
    GRAVACAO = "GRAVACAO"
    STATUS = "STATUS"
    IMPRESSAO = "IMPRESSAO"
    REENVIO = "REENVIO"
    ASSUMIR = "ASSUMIR"
    ACESSO_NEGADO = "ACESSO_NEGADO"
    ERRO = "ERRO"

    ACAO_CHOICES = [
        (LOGIN, "Login"),
        (FALHA_LOGIN, "Falha de login"),
        (LOGOUT, "Logout"),
        (GRAVACAO, "Gravacao"),
        (STATUS, "Alteracao de status"),
        (IMPRESSAO, "Impressao"),
        (REENVIO, "Reenvio"),
        (ASSUMIR, "Assumir atendimento"),
        (ACESSO_NEGADO, "Acesso negado"),
        (ERRO, "Erro"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="eventos_auditoria",
    )
    usuario_login = models.CharField(max_length=150, blank=True, default="", db_index=True)
    profissional = models.CharField(max_length=180, blank=True, default="", db_index=True)
    conselho = models.CharField(max_length=20, blank=True, default="")
    registro = models.CharField(max_length=60, blank=True, default="")

    acao = models.CharField(max_length=30, choices=ACAO_CHOICES, db_index=True)
    modulo = models.CharField(max_length=80, blank=True, default="", db_index=True)
    descricao = models.CharField(max_length=255, blank=True, default="")

    caminho = models.CharField(max_length=255, blank=True, default="")
    metodo = models.CharField(max_length=10, blank=True, default="")
    status_code = models.PositiveSmallIntegerField(blank=True, null=True, db_index=True)
    ip = models.GenericIPAddressField(blank=True, null=True)
    navegador = models.TextField(blank=True, default="")

    objeto_tipo = models.CharField(max_length=80, blank=True, default="")
    objeto_id = models.CharField(max_length=40, blank=True, default="", db_index=True)
    numero_bam = models.CharField(max_length=30, blank=True, default="", db_index=True)
    nome_paciente = models.CharField(max_length=200, blank=True, default="", db_index=True)
    dados = models.JSONField(blank=True, default=dict)

    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Evento de auditoria"
        verbose_name_plural = "Eventos de auditoria"
        indexes = [
            models.Index(fields=["criado_em", "acao"], name="aud_dt_acao_idx"),
            models.Index(fields=["modulo", "criado_em"], name="aud_mod_dt_idx"),
            models.Index(fields=["usuario_login", "criado_em"], name="aud_user_dt_idx"),
            models.Index(fields=["numero_bam", "criado_em"], name="aud_bam_dt_idx"),
        ]

    def __str__(self):
        autor = self.profissional or self.usuario_login or "Sistema"
        return f"{self.get_acao_display()} - {autor}"

    @property
    def profissional_com_registro(self):
        identificacao = self.profissional or self.usuario_login or "-"
        conselho = " ".join(
            item for item in [self.conselho, self.registro] if item
        )

        if conselho:
            return f"{identificacao} ({conselho})"

        return identificacao
