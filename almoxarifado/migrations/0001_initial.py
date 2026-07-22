from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MaterialAlmoxarifado",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(blank=True, db_index=True, default="", max_length=40)),
                ("nome", models.CharField(db_index=True, max_length=180)),
                ("categoria", models.CharField(choices=[("MATERIAL_HOSPITALAR", "Material hospitalar"), ("EPI", "EPI"), ("HIGIENE_LIMPEZA", "Higiene e limpeza"), ("ESCRITORIO", "Escritorio"), ("MANUTENCAO", "Manutencao"), ("NUTRICAO", "Nutricao"), ("ROUPARIA", "Rouparia"), ("OUTRO", "Outro")], db_index=True, default="MATERIAL_HOSPITALAR", max_length=40)),
                ("descricao", models.CharField(blank=True, default="", max_length=220)),
                ("marca", models.CharField(blank=True, default="", max_length=120)),
                ("unidade_medida", models.CharField(blank=True, default="unidade", max_length=50)),
                ("fornecedor", models.CharField(blank=True, default="", max_length=180)),
                ("localizacao", models.CharField(blank=True, default="", max_length=120)),
                ("estoque_atual", models.PositiveIntegerField(default=0)),
                ("estoque_minimo", models.PositiveIntegerField(default=0)),
                ("lote_atual", models.CharField(blank=True, default="", max_length=120)),
                ("validade", models.DateField(blank=True, null=True)),
                ("ativo", models.BooleanField(db_index=True, default=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Material do almoxarifado",
                "verbose_name_plural": "Materiais do almoxarifado",
                "ordering": ["categoria", "nome", "marca"],
            },
        ),
        migrations.CreateModel(
            name="MovimentacaoAlmoxarifado",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("ENTRADA", "Entrada"), ("SAIDA", "Saida"), ("AJUSTE", "Ajuste")], db_index=True, max_length=20)),
                ("quantidade", models.PositiveIntegerField()),
                ("saldo_anterior", models.PositiveIntegerField(default=0)),
                ("saldo_atual", models.PositiveIntegerField(default=0)),
                ("lote", models.CharField(blank=True, default="", max_length=120)),
                ("validade", models.DateField(blank=True, null=True)),
                ("setor_destino", models.CharField(blank=True, choices=[("", "---------"), ("Acolhimento", "Acolhimento"), ("Recepcao", "Recepcao"), ("Classificacao", "Classificacao"), ("Medico", "Medico"), ("Medicacao", "Medicacao"), ("Farmacia", "Farmacia"), ("Laboratorio", "Laboratorio"), ("Imagem", "Imagem"), ("Internacao", "Internacao"), ("Ambulancia", "Ambulancia"), ("Higienizacao", "Higienizacao"), ("Manutencao", "Manutencao"), ("Administrativo", "Administrativo"), ("Outro", "Outro")], db_index=True, default="", max_length=80)),
                ("origem_destino", models.CharField(blank=True, default="", max_length=180)),
                ("solicitante_nome", models.CharField(blank=True, default="", max_length=150)),
                ("profissional_nome", models.CharField(max_length=150)),
                ("profissional_registro", models.CharField(blank=True, default="", max_length=60)),
                ("observacao", models.TextField(blank=True, default="")),
                ("criado_em", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("material", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movimentacoes", to="almoxarifado.materialalmoxarifado")),
            ],
            options={
                "verbose_name": "Movimentacao do almoxarifado",
                "verbose_name_plural": "Movimentacoes do almoxarifado",
                "ordering": ["-criado_em"],
            },
        ),
        migrations.AddIndex(
            model_name="materialalmoxarifado",
            index=models.Index(fields=["ativo", "categoria", "nome"], name="almox_mat_cat_nome_idx"),
        ),
        migrations.AddIndex(
            model_name="materialalmoxarifado",
            index=models.Index(fields=["ativo", "validade"], name="almox_mat_valid_idx"),
        ),
        migrations.AddIndex(
            model_name="materialalmoxarifado",
            index=models.Index(fields=["codigo", "ativo"], name="almox_mat_cod_idx"),
        ),
        migrations.AddIndex(
            model_name="movimentacaoalmoxarifado",
            index=models.Index(fields=["material", "criado_em"], name="almox_mov_mat_dt_idx"),
        ),
        migrations.AddIndex(
            model_name="movimentacaoalmoxarifado",
            index=models.Index(fields=["tipo", "criado_em"], name="almox_mov_tipo_dt_idx"),
        ),
        migrations.AddIndex(
            model_name="movimentacaoalmoxarifado",
            index=models.Index(fields=["setor_destino", "criado_em"], name="almox_mov_setor_dt_idx"),
        ),
    ]
