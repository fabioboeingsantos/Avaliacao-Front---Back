"""Executa OpenRouter com fallback para Gemini usando a biblioteca Jangada."""

import json
import logging
import os

from ia.provedores.contrato import AssistenteIndisponivel
from ia.provedores.openrouter import obter_modelo


logger = logging.getLogger(__name__)


def chamar_agente(papel, instrucao, contexto, contrato):
    """Chama o modelo principal e usa Gemini quando a Jangada classificar falha recuperável."""
    chave_openrouter = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not chave_openrouter:
        raise AssistenteIndisponivel("Configure OPENROUTER_API_KEY para usar o assistente.")

    modelo_openrouter = obter_modelo(papel)
    modelo_gemini = os.getenv("IA_GEMINI_FALLBACK_MODEL", "gemini-3.8-flash").strip()
    chave_gemini = os.getenv("GEMINI_API_KEY", "").strip()

    try:
        # Importação tardia mantém o modo simulado disponível sem instalar Jangada.
        from jangada_ai import LLM

        # A restrição mantém o OpenRouter limitado a opções gratuitas também via Jangada.
        principal = LLM(
            "openrouter",
            modelo_openrouter,
            api_key=chave_openrouter,
            max_retries=1,
            extra={"provider": {"require_parameters": True, "max_price": {"prompt": 0, "completion": 0}}},
        )

        # A reserva recebe a mesma instrução e contrato, mas só é chamada em failover.
        reserva_opcoes = {"max_retries": 1}
        if chave_gemini:
            reserva_opcoes["api_key"] = chave_gemini
        reserva = LLM("gemini", modelo_gemini, **reserva_opcoes)

        # O sinalizador permite desligar o fallback sem alterar o fluxo principal.
        llm = principal.with_fallback(reserva) if os.getenv("IA_FALLBACK_JANGADA", "true").strip().lower() == "true" else principal

        # A Jangada valida a saída estruturada e tenta Gemini para falhas recuperáveis.
        resposta = llm.parse(
            prompt=json.dumps(contexto, ensure_ascii=False),
            schema=contrato,
            system=instrucao,
            params={"max_tokens": int(os.getenv("OPENROUTER_MAX_TOKENS", "2048"))},
        )
        if resposta.parsed is None:
            raise AssistenteIndisponivel("Os provedores não retornaram uma resposta estruturada válida.")

        # O log identifica o provedor que respondeu sem registrar mensagem ou credenciais.
        provedor_usado = getattr(resposta, "provider", None) or "provedor não identificado"
        logger.info("Agente %s respondido pelo provedor %s", papel, provedor_usado)
        return contrato.model_validate(resposta.parsed)
    except AssistenteIndisponivel:
        raise
    except Exception as erro:
        # Não expõe detalhes internos, chaves ou conteúdo do pedido na resposta HTTP.
        logger.warning("Falha nos provedores do agente %s (%s)", papel, type(erro).__name__)
        raise AssistenteIndisponivel("OpenRouter e Gemini não conseguiram concluir este agente.") from None
