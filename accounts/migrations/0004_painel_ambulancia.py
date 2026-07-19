from django.db import migrations


PAINEL = {
    "codigo": "ambulancia",
    "nome": "Solicitacao de Ambulancia",
    "descricao": "Remocao, transferencia e transporte de pacientes",
    "ordem": 140,
}


def criar_painel_ambulancia(apps, schema_editor):
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


def remover_painel_ambulancia(apps, schema_editor):
    PainelSistema = apps.get_model("accounts", "PainelSistema")
    PerfilAcesso = apps.get_model("accounts", "PerfilAcesso")

    PerfilAcesso.objects.filter(nome=PAINEL["nome"]).delete()
    PainelSistema.objects.filter(codigo=PAINEL["codigo"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_usuario_conselho_profissional"),
    ]

    operations = [
        migrations.RunPython(criar_painel_ambulancia, remover_painel_ambulancia),
    ]
