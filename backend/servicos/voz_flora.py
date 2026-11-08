"""Síntese da Flora com voz brasileira fixa e credencial restrita ao servidor."""

import base64
import binascii
import os

import httpx


VOZ_FLORA = "pt-BR-Chirp3-HD-Aoede"
IDIOMA_FLORA = "pt-BR"


class VozIndisponivel(Exception):
    """Falha de áudio que pode ser apresentada sem expor a resposta do provedor."""


def sintetizar(texto: str) -> dict:
    provedor = os.getenv("FLORA_VOZ_PROVEDOR", "navegador").strip().lower()
    if provedor == "navegador":
        return {"provedor": "navegador"}
    if provedor != "google":
        raise VozIndisponivel("A configuração de voz da Flora precisa ser revisada no servidor.")

    chave = os.getenv("GOOGLE_TTS_API_KEY", "").strip()
    if not chave:
        raise VozIndisponivel("A voz Aoede ainda não foi configurada. As respostas continuam disponíveis em texto.")

    try:
        with httpx.Client(timeout=30, follow_redirects=False) as cliente:
            resposta = cliente.post(
                "https://texttospeech.googleapis.com/v1/text:synthesize",
                headers={"X-Goog-Api-Key": chave},
                json={
                    "input": {"text": texto},
                    "voice": {"languageCode": IDIOMA_FLORA, "name": VOZ_FLORA},
                    "audioConfig": {"audioEncoding": "MP3"},
                },
            )
        if resposta.status_code in (400, 401, 403):
            raise VozIndisponivel("O Google recusou a geração de voz. Confira a chave, a API e o faturamento no servidor.")
        if resposta.status_code == 429:
            raise VozIndisponivel("O limite de geração de voz foi atingido. Tente ouvir novamente mais tarde.")
        resposta.raise_for_status()
        dados = resposta.json()
        conteudo = dados.get("audioContent") if isinstance(dados, dict) else None
        if not isinstance(conteudo, str) or not conteudo or len(conteudo) > 12_000_000:
            raise ValueError("Áudio inválido")
        base64.b64decode(conteudo, validate=True)
    except (httpx.HTTPError, ValueError, binascii.Error):
        raise VozIndisponivel("Não foi possível gerar a voz da Flora agora. Você pode continuar lendo a resposta.") from None

    return {"provedor": "google", "voz": VOZ_FLORA, "idioma": IDIOMA_FLORA,
            "tipo": "audio/mpeg", "audio": conteudo, "velocidade": 1.08}
