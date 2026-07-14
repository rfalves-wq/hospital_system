from unittest.mock import MagicMock, patch
from urllib import error as urlerror

from django.core.cache import cache
from django.test import SimpleTestCase
from django.urls import reverse


class CidadesPorUfTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_rejeita_uf_invalida(self):
        resposta = self.client.get(
            reverse("recepcao_cidades_por_uf", args=["XX"])
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(resposta.json()["erro"], "UF invalida.")

    @patch("recepcao.views.urlrequest.urlopen")
    def test_retorna_cidades_da_uf(self, urlopen):
        resposta_ibge = MagicMock()
        resposta_ibge.status = 200
        resposta_ibge.read.return_value = (
            b'[{"nome":"Bauru"},{"nome":"Araraquara"}]'
        )
        resposta_ibge.__enter__.return_value = resposta_ibge
        urlopen.return_value = resposta_ibge

        resposta = self.client.get(
            reverse("recepcao_cidades_por_uf", args=["SP"])
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.json(),
            [{"nome": "Araraquara"}, {"nome": "Bauru"}]
        )

    @patch("recepcao.views.urlrequest.urlopen")
    def test_retorna_resposta_controlada_quando_ibge_falha(self, urlopen):
        urlopen.side_effect = urlerror.URLError("offline")

        resposta = self.client.get(
            reverse("recepcao_cidades_por_uf", args=["SP"])
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.json()["erro"],
            "Nao foi possivel consultar as cidades."
        )
