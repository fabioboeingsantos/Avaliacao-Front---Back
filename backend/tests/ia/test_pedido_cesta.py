"""Testa a proposta de cesta sem acessar provedores externos ou gravar no banco."""

import json
from types import SimpleNamespace

import pytest

from ia import pedido_cesta
from ia.provedores.contrato import AssistenteIndisponivel


CATALOGO_FICTICIO = [
    {"id": "tomate", "nome": "Tomate", "estoque": 8, "categoria": "legumes", "preco_unitario": 2.0},
    {"id": "cebola", "nome": "Cebola", "estoque": 8, "categoria": "legumes", "preco_unitario": 1.0},
]


class LLMFalso:
    """Devolver uma saída estruturada controlada sem chamar a Jangada real."""

    def __init__(self, resposta):
        self.resposta = resposta
        self.argumentos = None

    def parse(self, **argumentos):
        """Guardar o contrato enviado ao modelo falso e devolver a resposta preparada."""
        self.argumentos = argumentos
        return SimpleNamespace(parsed=self.resposta)


def preparar_modelo(monkeypatch, resposta):
    """Preparar catálogo e cliente falsos para testar o caso de uso isoladamente."""
    cliente = LLMFalso(resposta)
    monkeypatch.setenv("ASSISTENTE_MODO", "openrouter")
    monkeypatch.setattr(pedido_cesta, "carregar_catalogo", lambda _sessao: CATALOGO_FICTICIO)
    monkeypatch.setattr(pedido_cesta, "criar_llm", lambda _papel: cliente)
    return cliente


def test_propor_cesta_retorna_proposta_validada_sem_enviar_preco_ou_conta(monkeypatch):
    """Confirmar uma proposta fictícia e limitar o contexto ao necessário."""
    cliente = preparar_modelo(monkeypatch, {
        "status": "proposta",
        "proposta": {
            "tipo": "pedido_cesta", "tamanho": "media", "modo": "selecionavel",
            "produtos": [{"produto_id": "tomate", "quantidade": 2}],
            "produtos_excluidos": ["cebola"],
        },
        "duvidas": [],
        "mensagem": "Confira a proposta.",
    })

    resultado = pedido_cesta.propor_cesta("Quero uma cesta média com 2 tomates, sem cebola.", object())

    assert resultado.status == "proposta"
    assert resultado.qa.status == "aprovado"
    assert resultado.proposta.produtos[0].produto_id == "tomate"
    contexto = json.loads(cliente.argumentos["prompt"])
    assert contexto["mensagem"].startswith("Quero uma cesta")
    assert contexto["catalogo_disponivel"][0] == {
        "id": "tomate", "nome": "Tomate", "estoque": 8, "categoria": "legumes",
    }
    assert "preco_unitario" not in cliente.argumentos["prompt"]
    assert cliente.argumentos["system"] == pedido_cesta.INSTRUCAO


def test_proposta_com_produto_fora_do_catalogo_pede_esclarecimento(monkeypatch):
    """Bloquear IDs que não existem no catálogo disponível."""
    preparar_modelo(monkeypatch, {
        "status": "proposta",
        "proposta": {
            "tipo": "pedido_cesta", "tamanho": "pequena", "modo": "selecionavel",
            "produtos": [{"produto_id": "abacaxi-ficticio", "quantidade": 1}],
            "produtos_excluidos": [],
        },
        "duvidas": [],
        "mensagem": "Confira.",
    })

    resultado = pedido_cesta.propor_cesta("Quero uma cesta pequena com abacaxi.", object())

    assert resultado.status == "esclarecimento"
    assert resultado.proposta is None
    assert resultado.qa.status == "esclarecimento"
    assert "fora do catálogo" in resultado.mensagem


def test_resposta_ambigua_volta_com_duvida_e_sem_proposta(monkeypatch):
    """Manter a proposta vazia quando o modelo pedir esclarecimento."""
    preparar_modelo(monkeypatch, {
        "status": "esclarecimento", "proposta": None,
        "duvidas": ["Qual tamanho de cesta você prefere?"],
        "mensagem": "Qual tamanho de cesta você prefere?",
    })

    resultado = pedido_cesta.propor_cesta("Quero uma cesta.", object())

    assert resultado.status == "esclarecimento"
    assert resultado.proposta is None
    assert resultado.qa.duvidas == ["Qual tamanho de cesta você prefere?"]


def test_tamanho_escrito_pela_pessoa_prevalece_sobre_tamanho_diferente_do_modelo(monkeypatch):
    """Preservar o tamanho explícito e validar os limites sem corrigir silenciosamente."""
    preparar_modelo(monkeypatch, {
        "status": "proposta",
        "proposta": {
            "tipo": "pedido_cesta", "tamanho": "media", "modo": "selecionavel",
            "produtos": [{"produto_id": "tomate", "quantidade": 1}],
            "produtos_excluidos": [],
        },
        "duvidas": [],
        "mensagem": "Confira.",
    })

    resultado = pedido_cesta.propor_cesta("Quero uma cesta pequena com tomate.", object())

    assert resultado.status == "proposta"
    assert resultado.proposta.tamanho == "pequena"


def test_falha_estruturada_vira_indisponibilidade_segura(monkeypatch):
    """Converter falha do cliente em erro seguro para a resposta HTTP 503."""
    cliente = LLMFalso(None)
    cliente.parse = lambda **_argumentos: SimpleNamespace(parsed=None)
    monkeypatch.setenv("ASSISTENTE_MODO", "openrouter")
    monkeypatch.setattr(pedido_cesta, "carregar_catalogo", lambda _sessao: CATALOGO_FICTICIO)
    monkeypatch.setattr(pedido_cesta, "criar_llm", lambda _papel: cliente)

    with pytest.raises(AssistenteIndisponivel, match="continue manualmente"):
        pedido_cesta.propor_cesta("Quero uma cesta fictícia.", object())
