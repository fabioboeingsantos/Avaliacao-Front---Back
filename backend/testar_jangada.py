"""Testa o fallback OpenRouter → Gemini com uma entrada fictícia."""

import json
import os

from ia.modelos import criar_llm
from ia.pedido_cesta import INSTRUCAO, RespostaModeloCesta


def executar_teste_fallback():
    """Forçar o 404 do modelo principal fictício e exibir qual provedor respondeu."""
    modelo_inexistente = os.getenv(
        "JANGADA_TESTE_MODELO_OPENROUTER",
        "provedor/modelo-inexistente:free",
    ).strip()
    if not modelo_inexistente.endswith(":free"):
        raise SystemExit("Use um identificador fictício terminado em :free para manter o teste gratuito.")

    # Usar um catálogo inventado para não expor dados reais do sistema ao provedor.
    contexto_ficticio = {
        "mensagem": "Quero uma cesta pequena com duas unidades de tomate e sem cebola.",
        "catalogo_disponivel": [
            {"id": "tomate", "nome": "Tomate", "estoque": 8, "categoria": "legumes"},
            {"id": "cebola", "nome": "Cebola", "estoque": 6, "categoria": "legumes"},
        ],
        "regras_cesta": {
            "limites": {"pequena": 5, "media": 8, "grande": 12},
            "maximo_unidades": 10,
        },
    }

    # Criar a cadeia atual com o modelo OpenRouter inexistente como teste controlado.
    llm = criar_llm("pedido_cesta", modelo_openrouter=modelo_inexistente)
    try:
        resposta = llm.parse(
            prompt=json.dumps(contexto_ficticio, ensure_ascii=False),
            schema=RespostaModeloCesta,
            system=INSTRUCAO,
            params={"max_tokens": 1024},
        )
    except Exception as erro:
        # Exibir somente o tipo do erro para não revelar conteúdo ou credenciais.
        raise SystemExit(f"O fallback não concluiu o teste ({type(erro).__name__}).") from None

    if resposta.parsed is None:
        raise SystemExit("Os provedores não retornaram uma resposta estruturada válida.")

    # Mostrar o provedor vencedor sem imprimir chaves ou dados reais.
    print(f"Modelo principal de teste: {modelo_inexistente}")
    print(f"Provedor que respondeu: {getattr(resposta, 'provider', 'não identificado')}")
    print(f"Modelo que respondeu: {getattr(resposta, 'model', 'não identificado')}")
    print(RespostaModeloCesta.model_validate(resposta.parsed).model_dump_json(indent=2))


if __name__ == "__main__":
    executar_teste_fallback()
