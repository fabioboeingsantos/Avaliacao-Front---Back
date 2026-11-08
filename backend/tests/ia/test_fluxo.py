"""Validação local deve prevalecer sobre uma aprovação incorreta do modelo."""

import pytest

from ia.fluxo import analisar_agentes


@pytest.mark.parametrize("alteracoes", [
    {"tamanho": None, "modo": "pronta"},
    {"produtos": [{"produto_id": "inventado", "quantidade": 1}]},
    {"produtos_excluidos": ["tomate"]},
    {"tipo": "separacao", "cesta_id": 99},
])
def test_aprovacao_da_ia_nao_libera_proposta_invalida(alteracoes):
    proposta = {"tipo": "pedido_cesta", "tamanho": "media",
                "produtos": [{"produto_id": "tomate", "quantidade": 1}], **alteracoes}
    chamadas = []

    def chamar(papel, instrucao, contexto, contrato):
        chamadas.append(papel)
        respostas = {
            "interprete": {"intencao": "Montar cesta", "fora_do_escopo": False},
            "assinante": {"proposta": proposta, "mensagem": "Confira.", "pergunta": None},
            "qa": {"status": "aprovado", "problemas": [], "duvidas": []},
        }
        return contrato.model_validate(respostas[papel])

    resultado = analisar_agentes("Quero uma cesta", "assinante",
                                [{"id": "tomate", "estoque": 10}], [],
                                chamar_agente=chamar, modo="openrouter")
    assert chamadas == ["interprete", "assinante", "qa"]
    assert resultado["qa"]["status"] == "bloqueado"
    assert resultado["proposta"] is None


def test_perfil_desconhecido_nao_chama_modelo():
    def nao_chamar(*args):
        pytest.fail("Perfil inválido não deve chamar o provedor.")

    with pytest.raises(ValueError, match="Perfil"):
        analisar_agentes("Uma cesta", "administrador", [], [],
                         chamar_agente=nao_chamar, modo="openrouter")
