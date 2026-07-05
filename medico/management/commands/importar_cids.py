import csv
import io
import os
import re

from django.core.management.base import BaseCommand

from medico.models import CID


class Command(BaseCommand):
    help = "Importa CIDs a partir de CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "arquivo",
            type=str,
            help="Caminho do arquivo CSV"
        )

        parser.add_argument(
            "--tipo",
            type=str,
            default="SUBCATEGORIA",
            help="Tipo do CID: CAPITULO, GRUPO, CATEGORIA ou SUBCATEGORIA"
        )

    def abrir_csv(self, caminho):
        encodings = [
            "utf-8-sig",
            "utf-8",
            "latin-1",
            "cp1252",
        ]

        for encoding in encodings:
            try:
                with open(caminho, "r", encoding=encoding, newline="") as arquivo:
                    conteudo = arquivo.read()

                return io.StringIO(conteudo)

            except UnicodeDecodeError:
                continue

        raise UnicodeDecodeError(
            "encoding",
            b"",
            0,
            1,
            "Não foi possível ler o arquivo."
        )

    def normalizar_codigo(self, codigo):
        codigo = (codigo or "").strip().upper()

        codigo = codigo.replace(" ", "")
        codigo = codigo.replace("-", "")
        codigo = codigo.replace("_", "")

        if re.match(r"^[A-Z][0-9]{3}$", codigo):
            codigo = f"{codigo[:3]}.{codigo[3]}"

        return codigo

    def handle(self, *args, **options):
        caminho_arquivo = options["arquivo"]
        tipo = options["tipo"].upper()

        tipos_validos = [
            "CAPITULO",
            "GRUPO",
            "CATEGORIA",
            "SUBCATEGORIA",
        ]

        if tipo not in tipos_validos:
            self.stdout.write(
                self.style.ERROR(
                    "Tipo inválido. Use CAPITULO, GRUPO, CATEGORIA ou SUBCATEGORIA."
                )
            )
            return

        if not os.path.exists(caminho_arquivo):
            self.stdout.write(
                self.style.ERROR(
                    f"Arquivo não encontrado: {caminho_arquivo}"
                )
            )
            return

        arquivo = self.abrir_csv(caminho_arquivo)

        leitor = csv.DictReader(
            arquivo,
            delimiter=";"
        )

        total_criados = 0
        total_atualizados = 0
        total_ignorados = 0

        for linha in leitor:
            codigo = (
                linha.get("Codigo")
                or linha.get("CODIGO")
                or linha.get("codigo")
                or ""
            )

            descricao = (
                linha.get("DESCRICAO")
                or linha.get("Descrição")
                or linha.get("descricao")
                or linha.get("DESCR")
                or ""
            )

            codigo = self.normalizar_codigo(codigo)
            descricao = (descricao or "").strip()

            if not codigo or not descricao:
                total_ignorados += 1
                continue

            cid, criado = CID.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "descricao": descricao,
                    "tipo": tipo,
                }
            )

            if criado:
                total_criados += 1
            else:
                total_atualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Importação finalizada. Criados: {total_criados}. Atualizados: {total_atualizados}. Ignorados: {total_ignorados}."
            )
        )