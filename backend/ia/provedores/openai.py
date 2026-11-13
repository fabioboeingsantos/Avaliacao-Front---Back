"""Chamada estruturada à API da OpenAI."""

import json
import os

import httpx

from ia.provedores.contrato import AssistenteIndisponivel
from ia.provedores.esquema import schema_estrito


def chamar_agente(papel, instrucao, contexto, contrato):
    chave = os.getenv("OPENAI_API_KEY", "").strip()
    if not chave:
        raise AssistenteIndisponivel("Configure OPENAI_API_KEY para o agente atribuído à OpenAI.")

    modelo = os.getenv(f"IA_MODELO_{papel.upper()}", "").strip() or os.getenv("IA_MODELO_PADRAO", "").strip()
    if not modelo:
        raise AssistenteIndisponivel("Configure o modelo IA_MODELO do agente atribuído à OpenAI.")

    try:
        resposta = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {chave}"},
            json={
                "model": modelo,
                "messages": [
                    {"role": "system", "content": instrucao + "\nRetorne somente JSON conforme o schema."},
                    {"role": "user", "content": json.dumps(contexto, ensure_ascii=False)},
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": f"agente_{papel}",
                        "strict": True,
                        "schema": schema_estrito(contrato.model_json_schema()),
                    },
                },
            },
            timeout=40,
            follow_redirects=False,
        )
        resposta.raise_for_status()
        texto = resposta.json()["choices"][0]["message"]["content"]
        return contrato.model_validate_json(texto)
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        raise AssistenteIndisponivel("A OpenAI não concluiu uma resposta válida para este agente.") from None
