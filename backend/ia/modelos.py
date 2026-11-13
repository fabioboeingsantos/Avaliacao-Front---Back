"""Configura os provedores usados pela Flora por meio da biblioteca Jangada."""

import os

from ia.provedores.openrouter import obter_modelo
from ia.provedores.contrato import AssistenteIndisponivel


def criar_llm(papel: str = "interprete", modelo_openrouter: str | None = None):
    """Criar a cadeia atual OpenRouter → Gemini sem incluir um provedor pago."""

    chave_openrouter = os.getenv("OPENROUTER_API_KEY", "").strip()
    chave_gemini = os.getenv("GEMINI_API_KEY", "").strip()
    if not chave_openrouter:
        raise AssistenteIndisponivel("Configure OPENROUTER_API_KEY para usar o assistente.")

    modelo_openrouter = modelo_openrouter or obter_modelo(papel)
    if modelo_openrouter != "openrouter/free" and not modelo_openrouter.endswith(":free"):
        raise AssistenteIndisponivel("Configure openrouter/free ou um modelo terminado em :free para este projeto.")
    modelo_gemini = os.getenv("IA_GEMINI_FALLBACK_MODEL", "gemini-3.8-flash").strip()
    if not modelo_gemini:
        raise AssistenteIndisponivel("Configure IA_GEMINI_FALLBACK_MODEL para o provedor de reserva.")

    # Importar a Jangada dentro da função mantém os modos locais disponíveis sem inicializar provedores.
    from jangada_ai import LLM

    # Restringir a OpenRouter gratuita para evitar que a reserva use um modelo pago.
    principal = LLM(
        "openrouter",
        modelo_openrouter,
        api_key=chave_openrouter,
        max_retries=1,
        extra={"provider": {"require_parameters": True, "max_price": {"prompt": 0, "completion": 0}}},
    )

    # Usar Gemini como fallback depois da OpenRouter, conforme o arranjo já presente no projeto.
    opcoes_reserva = {"max_retries": 1}
    if chave_gemini:
        opcoes_reserva["api_key"] = chave_gemini
    reserva = LLM("gemini", modelo_gemini, **opcoes_reserva)

    # Permitir desligar o fallback por configuração sem mudar a ordem dos provedores.
    if os.getenv("IA_FALLBACK_JANGADA", "true").strip().lower() == "true":
        return principal.with_fallback(reserva)
    return principal
