from django.db import migrations, models


PAINEL = {
    "codigo": "funcionarios",
    "nome": "Funcionarios",
    "descricao": "Cadastro, conselho, setores e escala de profissionais",
    "ordem": 160,
}


def criar_painel_funcionarios(apps, schema_editor):
    PainelSistema = apps.get_model("accounts", "PainelSistema")
    PerfilAcesso = apps.get_model("accounts", "PerfilAcesso")

    painel, _criado = PainelSistema.objects.update_or_create(
        codigo=PAINEL["codigo"],
        defaults={
            "nome": PAINEL["nome"],
            "descricao": PAINEL["descricao"],
            "ordem": PAINEL["ordem"],
            "ativo": True,
        },
    )
    perfil, _criado = PerfilAcesso.objects.update_or_create(
        nome=PAINEL["nome"],
        defaults={
            "descricao": PAINEL["descricao"],
            "ativo": True,
        },
    )
    perfil.paineis.set([painel])

    perfil_admin = PerfilAcesso.objects.filter(nome="Administrador do sistema").first()
    if perfil_admin:
        perfil_admin.paineis.add(painel)


def remover_painel_funcionarios(apps, schema_editor):
    PainelSistema = apps.get_model("accounts", "PainelSistema")
    PerfilAcesso = apps.get_model("accounts", "PerfilAcesso")

    PerfilAcesso.objects.filter(nome=PAINEL["nome"]).delete()
    PainelSistema.objects.filter(codigo=PAINEL["codigo"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_painel_auditoria"),
    ]

    operations = [
        migrations.AlterField(
            model_name="painelsistema",
            name="codigo",
            field=models.CharField(
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
                    ("ambulancia", "Solicitacao de Ambulancia"),
                    ("auditoria", "Auditoria do Sistema"),
                    ("funcionarios", "Funcionarios"),
                ],
                max_length=40,
                unique=True,
                verbose_name="Painel",
            ),
        ),
        migrations.RunPython(criar_painel_funcionarios, remover_painel_funcionarios),
    ]
