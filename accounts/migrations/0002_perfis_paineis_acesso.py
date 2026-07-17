from django.db import migrations, models


PAINEIS_PADRAO = [
    ("acolhimento", "Acolhimento", "Entrada e tipo de atendimento do paciente", 10),
    ("recepcao", "Recepcao", "Cadastro, recepcao e encaminhamento do paciente", 20),
    ("classificacao", "Classificacao de risco", "Classificacao de risco e chamadas do setor", 30),
    ("medico", "Medico", "Fila medica, consulta e retorno", 40),
    ("prontuario", "Prontuario", "Consulta do prontuario do paciente", 50),
    ("medicacao", "Sala de medicacao", "Administracao de medicacoes", 60),
    ("farmacia", "Farmacia", "Estoque, farmacia e dispensacao", 70),
    ("internacao", "Internacao", "Leitos, internacao e acompanhamento", 80),
    ("laboratorio", "Laboratorio", "Solicitacoes e resultados laboratoriais", 90),
    ("imagem", "Imagem", "Exames de imagem e resultados", 100),
    ("ti", "Tecnologia da Informacao", "Equipamentos, rede e chamados do TI", 110),
    ("suporte_ti", "Solicitar TI", "Abrir e acompanhar chamados para a area de TI", 120),
    ("painel_chamados", "Painel de chamados", "Painel publico de chamadas de pacientes", 130),
]


def criar_paineis_e_perfis(apps, schema_editor):
    PainelSistema = apps.get_model("accounts", "PainelSistema")
    PerfilAcesso = apps.get_model("accounts", "PerfilAcesso")

    paineis = []

    for codigo, nome, descricao, ordem in PAINEIS_PADRAO:
        painel, _criado = PainelSistema.objects.update_or_create(
            codigo=codigo,
            defaults={
                "nome": nome,
                "descricao": descricao,
                "ordem": ordem,
                "ativo": True,
            },
        )
        paineis.append(painel)

        perfil, _criado = PerfilAcesso.objects.update_or_create(
            nome=nome,
            defaults={
                "descricao": descricao,
                "ativo": True,
            },
        )
        perfil.paineis.set([painel])

    perfil_admin, _criado = PerfilAcesso.objects.update_or_create(
        nome="Administrador do sistema",
        defaults={
            "descricao": "Acesso completo aos paineis do sistema",
            "ativo": True,
        },
    )
    perfil_admin.paineis.set(paineis)


def remover_paineis_e_perfis(apps, schema_editor):
    PainelSistema = apps.get_model("accounts", "PainelSistema")
    PerfilAcesso = apps.get_model("accounts", "PerfilAcesso")

    codigos = [codigo for codigo, _nome, _descricao, _ordem in PAINEIS_PADRAO]
    nomes = [nome for _codigo, nome, _descricao, _ordem in PAINEIS_PADRAO]
    nomes.append("Administrador do sistema")

    PerfilAcesso.objects.filter(nome__in=nomes).delete()
    PainelSistema.objects.filter(codigo__in=codigos).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PainelSistema",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "codigo",
                    models.CharField(
                        choices=[
                            ("acolhimento", "Acolhimento"),
                            ("recepcao", "Recepcao"),
                            ("classificacao", "Classificacao de risco"),
                            ("medico", "Medico"),
                            ("prontuario", "Prontuario"),
                            ("medicacao", "Sala de medicacao"),
                            ("farmacia", "Farmacia"),
                            ("internacao", "Internacao"),
                            ("laboratorio", "Laboratorio"),
                            ("imagem", "Imagem"),
                            ("ti", "Tecnologia da Informacao"),
                            ("suporte_ti", "Solicitar TI"),
                            ("painel_chamados", "Painel de chamados"),
                        ],
                        max_length=40,
                        unique=True,
                        verbose_name="Painel",
                    ),
                ),
                ("nome", models.CharField(max_length=120)),
                ("descricao", models.CharField(blank=True, default="", max_length=255)),
                ("ordem", models.PositiveSmallIntegerField(default=0)),
                ("ativo", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Painel do sistema",
                "verbose_name_plural": "Paineis do sistema",
                "ordering": ["ordem", "nome"],
            },
        ),
        migrations.CreateModel(
            name="PerfilAcesso",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome", models.CharField(max_length=120, unique=True)),
                ("descricao", models.CharField(blank=True, default="", max_length=255)),
                ("ativo", models.BooleanField(default=True)),
                (
                    "paineis",
                    models.ManyToManyField(
                        blank=True,
                        related_name="perfis",
                        to="accounts.painelsistema",
                        verbose_name="Paineis liberados",
                    ),
                ),
            ],
            options={
                "verbose_name": "Perfil de acesso",
                "verbose_name_plural": "Perfis de acesso",
                "ordering": ["nome"],
            },
        ),
        migrations.AddField(
            model_name="usuario",
            name="paineis_extra",
            field=models.ManyToManyField(
                blank=True,
                related_name="usuarios_com_acesso_extra",
                to="accounts.painelsistema",
                verbose_name="Paineis extras",
            ),
        ),
        migrations.AddField(
            model_name="usuario",
            name="perfis_acesso",
            field=models.ManyToManyField(
                blank=True,
                related_name="usuarios",
                to="accounts.perfilacesso",
                verbose_name="Perfis de acesso",
            ),
        ),
        migrations.RunPython(criar_paineis_e_perfis, remover_paineis_e_perfis),
    ]
