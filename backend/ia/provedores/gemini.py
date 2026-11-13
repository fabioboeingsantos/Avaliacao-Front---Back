"""Chamada estruturada à Gemini API."""

import json
import os

import httpx

from ia.provedores.contrato import AssistenteIndisponivel
from ia.provedores.esquema import schema_estrito


def chamar_agente(papel, instrucao, contexto, contrato):
    chave = os.getenv("GEMINI_API_KEY", "").strip()
    if not chave:
        raise AssistenteIndisponivel("Configure GEMINI_API_KEY para o agente atribuído ao Gemini.")

    modelo = os.getenv(f"IA_MODELO_{papel.upper()}", "").strip() or os.getenv("IA_MODELO_PADRAO", "").strip()
    if not modelo:
        raise AssistenteIndisponivel("Configure o modelo IA_MODELO do agente atribuído ao Gemini.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    try:
        resposta = httpx.post(
            url,
            headers={"x-goog-api-key": chave},
            json={
                "systemInstruction": {"parts": [{"text": instrucao + "\nRetorne somente JSON conforme o schema."}]},
                "contents": [{"role": "user", "parts": [{"text": json.dumps(contexto, ensure_ascii=False)}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "responseJsonSchema": schema_estrito(contrato.model_json_schema()),
                },
            },
            timeout=40,
            follow_redirects=False,
        )
        resposta.raise_for_status()
        texto = resposta.json()["candidates"][0]["content"]["parts"][0]["text"]
        return contrato.model_validate_json(texto)
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        raise AssistenteIndisponivel("O Gemini não concluiu uma resposta válida para este agente.") from None
