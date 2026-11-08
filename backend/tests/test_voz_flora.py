"""Verificações isoladas: nenhum acesso ao Google ou ao banco de dados."""

import base64
import os
import unittest
from unittest.mock import patch

import httpx
from pydantic import ValidationError

from esquemas.voz import EntradaVoz
from servicos import voz_flora


class TestVozFlora(unittest.TestCase):
    def test_modo_navegador_nao_chama_google(self):
        with patch.dict(os.environ, {"FLORA_VOZ_PROVEDOR": "navegador"}), \
                patch.object(voz_flora.httpx, "Client") as cliente:
            self.assertEqual(voz_flora.sintetizar("Olá"), {"provedor": "navegador"})
            cliente.assert_not_called()

    def test_google_sem_chave_nao_chama_servico_nem_substitui_voz(self):
        with patch.dict(os.environ, {"FLORA_VOZ_PROVEDOR": "google", "GOOGLE_TTS_API_KEY": ""}), \
                patch.object(voz_flora.httpx, "Client") as cliente:
            with self.assertRaises(voz_flora.VozIndisponivel):
                voz_flora.sintetizar("Olá")
            cliente.assert_not_called()

    def sintetizar_com_resposta(self, status, corpo):
        capturas = []
        def responder(requisicao):
            capturas.append(requisicao)
            return httpx.Response(status, json=corpo)
        cliente = httpx.Client(transport=httpx.MockTransport(responder))
        with patch.dict(os.environ, {"FLORA_VOZ_PROVEDOR": "google", "GOOGLE_TTS_API_KEY": "chave-ficticia"}), \
                patch.object(voz_flora.httpx, "Client", return_value=cliente):
            resultado = voz_flora.sintetizar("Olá, sou a Flora.")
        return resultado, capturas

    def test_voz_idioma_e_credencial_ficam_fixos_no_backend(self):
        import json
        audio = base64.b64encode(b"audio-de-teste").decode()
        resultado, pedidos = self.sintetizar_com_resposta(200, {"audioContent": audio})
        self.assertEqual(len(pedidos), 1)
        pedido = pedidos[0]
        self.assertEqual(json.loads(pedido.content)["voice"],
                         {"languageCode": "pt-BR", "name": "pt-BR-Chirp3-HD-Aoede"})
        self.assertNotIn("chave-ficticia", str(pedido.url))
        self.assertEqual(pedido.headers["X-Goog-Api-Key"], "chave-ficticia")
        self.assertEqual(resultado["velocidade"], 1.08)
        self.assertNotIn("chave-ficticia", str(resultado))

    def test_falhas_do_google_nao_vazam_detalhes(self):
        for status in (401, 403, 429, 500):
            with self.subTest(status=status):
                with self.assertRaises(voz_flora.VozIndisponivel) as falha:
                    self.sintetizar_com_resposta(status, {"error": "detalhe-secreto-do-provedor"})
                self.assertNotIn("detalhe-secreto", str(falha.exception))

    def test_audio_invalido_nao_e_retornado(self):
        for corpo in ({}, [], {"audioContent": "não é base64"}):
            with self.subTest(corpo=corpo):
                with self.assertRaises(voz_flora.VozIndisponivel):
                    self.sintetizar_com_resposta(200, corpo)

    def test_limite_de_bytes_inclui_acentos(self):
        self.assertEqual(EntradaVoz(texto="á" * 2250).texto, "á" * 2250)
        for texto in (" ", "á" * 2251):
            with self.assertRaises(ValidationError):
                EntradaVoz(texto=texto)


if __name__ == "__main__":
    unittest.main()
