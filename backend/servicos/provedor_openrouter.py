"""OpenRouter para o projeto de sala: somente modelos gratuitos, sem retries."""

import json
import os

import httpx

from servicos.provedor_ia import AssistenteIndisponivel


def _schema_estrito(schema):
    """Explicita todos os campos para provedores com saída estruturada estrita."""
    if isinstance(schema, list):
        return [_schema_estrito(item) for item in schema]
    if not isinstance(schema, dict):
        return schema
    resultado = {chave: _schema_estrito(valor) for chave, valor in schema.items() if chave != "default"}
    if resultado.get("type") == "object":
        resultado["additionalProperties"] = False
        resultado["required"] = list(resultado.get("properties", {}))
    return resultado


def obter_modelo(papel):
    modelo = (os.getenv(f"OPENROUTER_MODEL_{papel.upper()}") or
              os.getenv("OPENROUTER_MODEL") or "openrouter/free").strip()
    if modelo != "openrouter/free" and not modelo.endswith(":free"):
        raise AssistenteIndisponivel("Configure openrouter/free ou um modelo terminado em :free para este projeto.")
    return modelo


def chamar_agente(papel, instrucao, contexto, contrato):
    chave = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not chave:
        raise AssistenteIndisponivel("Configure OPENROUTER_API_KEY no .env do backend para usar a OpenRouter.")
    modelo = obter_modelo(papel)
    try:
        timeout = max(1, min(float(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "40")), 60))
        tokens = max(256, min(int(os.getenv("OPENROUTER_MAX_TOKENS", "2048")), 8192))
    except ValueError:
        raise AssistenteIndisponivel("Confira os limites de tempo e tokens da OpenRouter no backend.") from None
    corpo = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": instrucao + "\nRetorne somente um objeto JSON conforme este schema: " + json.dumps(contrato.model_json_schema(), ensure_ascii=False)},
            {"role": "user", "content": json.dumps(contexto, ensure_ascii=False)},
        ],
        "response_format": {"type": "json_schema", "json_schema": {
            "name": f"agente_{papel}", "strict": True,
            "schema": _schema_estrito(contrato.model_json_schema()),
        }},
        "max_tokens": tokens,
        "reasoning": {"enabled": False},
        "stream": False,
        "provider": {"require_parameters": True, "max_price": {"prompt": 0, "completion": 0}},
    }
    try:
        with httpx.Client(timeout=timeout, follow_redirects=False) as cliente:
            resposta = cliente.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {chave}"}, json=corpo,
            )
        if resposta.status_code in (401, 403):
            raise AssistenteIndisponivel("A OpenRouter recusou o acesso. Confira a chave e as permissões da conta.")
        if resposta.status_code == 402:
            raise AssistenteIndisponivel("A OpenRouter bloqueou a conta por saldo ou orçamento. Confira o painel; não houve troca para um modelo pago.")
        if resposta.status_code == 429:
            raise AssistenteIndisponivel("A cota da OpenRouter foi atingida. Aguarde a renovação do limite ou continue manualmente.")
        if resposta.status_code in (404, 502, 503):
            raise AssistenteIndisponivel("Nenhum modelo gratuito compatível está disponível agora. Tente depois ou continue manualmente.")
        resposta.raise_for_status()
        escolha = resposta.json()["choices"][0]
        if escolha["finish_reason"] != "stop":
            raise AssistenteIndisponivel("A OpenRouter não concluiu a resposta. Continue manualmente ou tente novamente.")
        return contrato.model_validate_json(escolha["message"]["content"])
    except (httpx.HTTPError, httpx.InvalidURL, KeyError, IndexError, TypeError, ValueError):
        raise AssistenteIndisponivel("Não foi possível validar a resposta da OpenRouter. Tente novamente ou continue manualmente.") from None
