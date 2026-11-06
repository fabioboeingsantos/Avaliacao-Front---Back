"""Cliente Moonshot isolado: credenciais e respostas externas ficam no backend."""

import json
import os

import httpx
from pydantic import ValidationError
from servicos.provedor_ia import AssistenteIndisponivel


class KimiIndisponivel(AssistenteIndisponivel):
    """Erro seguro para a interface, sem cabeçalhos ou resposta do provedor."""


def chamar_agente(papel, instrucao, contexto, contrato):
    chave = os.getenv("KIMI_API_KEY", "").strip()
    if not chave:
        raise KimiIndisponivel("Configure KIMI_API_KEY no backend para usar o assistente Kimi.")
    base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1").rstrip("/")
    if not base_url.startswith("https://"):
        raise KimiIndisponivel("KIMI_BASE_URL precisa usar HTTPS.")
    modelo = os.getenv(f"KIMI_MODEL_{papel.upper()}") or os.getenv("KIMI_MODEL", "kimi-k3")
    try:
        timeout = max(1, min(float(os.getenv("KIMI_TIMEOUT_SECONDS", "40")), 60))
        tokens = max(256, min(int(os.getenv("KIMI_MAX_COMPLETION_TOKENS", "4096")), 8192))
    except ValueError:
        raise KimiIndisponivel("Confira os limites de tempo e tokens do Kimi no backend.") from None
    corpo = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": instrucao + "\nRetorne somente JSON conforme este schema: " + json.dumps(contrato.model_json_schema(), ensure_ascii=False)},
            {"role": "user", "content": json.dumps(contexto, ensure_ascii=False)},
        ],
        "response_format": {"type": "json_object"},
        "max_completion_tokens": tokens,
        "stream": False,
    }
    if modelo == "kimi-k3":
        corpo["reasoning_effort"] = "low"
    try:
        # Sem retries automáticos: cada tentativa pode consumir a cota da conta.
        with httpx.Client(timeout=timeout, follow_redirects=False) as cliente:
            resposta = cliente.post(base_url + "/chat/completions", headers={"Authorization": f"Bearer {chave}"}, json=corpo)
        if resposta.status_code in (401, 403):
            raise KimiIndisponivel("A chave ou o modelo Kimi não tem acesso. Confira a configuração no provedor.")
        if resposta.status_code in (402, 429):
            raise KimiIndisponivel("O Kimi atingiu um limite de uso ou saldo. Tente depois ou continue manualmente.")
        resposta.raise_for_status()
        escolha = resposta.json()["choices"][0]
        if escolha["finish_reason"] != "stop":
            raise KimiIndisponivel("O Kimi não concluiu a resposta. Tente novamente ou continue manualmente.")
        return contrato.model_validate_json(escolha["message"]["content"])
    except (httpx.HTTPError, httpx.InvalidURL, KeyError, IndexError, TypeError, ValueError, ValidationError):
        raise KimiIndisponivel("Não foi possível concluir a análise com o Kimi. Tente novamente ou continue manualmente.") from None
