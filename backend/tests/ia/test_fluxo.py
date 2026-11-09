"""Validação local e auditoria do agente de QA sobre propostas e impedimentos."""

import pytest

from ia.fluxo import analisar_agentes
from ia.provedores import simulado


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


def test_proposta_nula_preserva_motivo_especifico_do_qa():
    cesta_enviada = {
        "id": 901, "tamanho": "pequena", "modo": "selecionavel", "situacao": "Enviado",
        "separacao_concluida_em": "2026-11-04T12:00:00",
        "produtos": [{"id": "tomate", "quantidade": 2}], "separacoes": [],
    }
    auditoria_capturada = {}

    def chamar(papel, instrucao, contexto, contrato):
        if papel == "qa":
            auditoria_capturada.update(contexto.get("auditoria_qa", {}))
        respostas = {
            "interprete": {"intencao": "Separar cesta 901", "fora_do_escopo": False},
            "produtor": {"proposta": None, "mensagem": "A cesta 901 já foi enviada.", "pergunta": None},
            "qa": {"status": "bloqueado", "problemas": ["A cesta 901 já foi enviada e não pode ser separada."], "duvidas": []},
        }
        return contrato.model_validate(respostas[papel])

    resultado = analisar_agentes(
        "Separe mais 1 tomate na cesta 901.", "produtor",
        [{"id": "tomate", "estoque": 10}], [cesta_enviada],
        chamar_agente=chamar, modo="openrouter",
    )
    assert auditoria_capturada["status_sugerido"] == "bloqueado"
    assert resultado["proposta"] is None
    assert resultado["qa"]["status"] == "bloqueado"
    assert "A cesta 901 já foi enviada e não pode ser separada." in resultado["qa"]["problemas"]
    assert "A solicitação ainda não tem uma proposta completa." not in resultado["qa"]["problemas"]


def test_proposta_nula_preserva_esclarecimento_e_duvida_do_qa():
    def chamar(papel, instrucao, contexto, contrato):
        respostas = {
            "interprete": {"intencao": "Pedir cesta pronta", "fora_do_escopo": False},
            "assinante": {
                "proposta": None,
                "mensagem": "Preciso saber o tamanho da cesta pronta.",
                "pergunta": "Qual tamanho de cesta pronta você deseja: pequena, média ou grande?",
            },
            "qa": {
                "status": "esclarecimento",
                "problemas": [],
                "duvidas": ["Qual tamanho de cesta pronta você deseja: pequena, média ou grande?"],
            },
        }
        return contrato.model_validate(respostas[papel])

    resultado = analisar_agentes(
        "Quero uma cesta pronta.", "assinante",
        [{"id": "tomate", "estoque": 10}], [],
        chamar_agente=chamar, modo="openrouter",
    )
    assert resultado["proposta"] is None
    assert resultado["qa"]["status"] == "esclarecimento"
    assert resultado["qa"]["duvidas"] == ["Qual tamanho de cesta pronta você deseja: pequena, média ou grande?"]
    assert not resultado["qa"]["problemas"]


def test_cesta_selecionavel_calcula_tamanho_automaticamente_pelos_itens():
    catalogo = [
        {"id": "tomate", "nome": "Tomate", "estoque": 10},
        {"id": "cenoura", "nome": "Cenoura", "estoque": 10},
        {"id": "cebola", "nome": "Cebola", "estoque": 10},
    ]

    def chamar(papel, instrucao, contexto, contrato):
        respostas = {
            "interprete": {"intencao": "Montar cesta selecionável", "fora_do_escopo": False},
            "assinante": {
                "proposta": {
                    "tipo": "pedido_cesta", "tamanho": None, "modo": "selecionavel",
                    "produtos": [
                        {"produto_id": "tomate", "quantidade": 2},
                        {"produto_id": "cenoura", "quantidade": 1},
                    ],
                    "produtos_excluidos": ["cebola"],
                },
                "mensagem": "Montei sua cesta.",
                "pergunta": "Qual tamanho de cesta deseja?",
            },
            "qa": {"status": "aprovado", "problemas": [], "duvidas": []},
        }
        return contrato.model_validate(respostas[papel])

    resultado = analisar_agentes(
        "Quero 2 tomates e 1 cenoura, sem cebola.", "assinante",
        catalogo, [], chamar_agente=chamar, modo="openrouter",
    )
    assert resultado["status"] == "proposta"
    assert resultado["qa"]["status"] == "aprovado"
    assert resultado["proposta"]["modo"] == "selecionavel"
    assert resultado["proposta"]["tamanho"] == "pequena"
    assert resultado["proposta"]["produtos_excluidos"] == ["cebola"]


def test_conflito_tamanho_pequena_com_seis_produtos_nao_aumenta_silenciosamente():
    nomes = ("tomate", "cenoura", "cebola", "alface", "batata", "couve")
    catalogo = [{"id": n, "nome": n.title(), "estoque": 10} for n in nomes]
    mensagem = (
        "Quero uma cesta pequena selecionável com 1 tomate, 1 cenoura, 1 cebola, "
        "1 alface, 1 batata e 1 couve. Quero manter esses seis produtos."
    )
    auditoria_capturada = {}

    def chamar(papel, instrucao, contexto, contrato):
        if papel == "qa":
            auditoria_capturada.update(contexto.get("auditoria_qa", {}))
        respostas = {
            "interprete": {"intencao": "Montar cesta pequena com 6 itens", "fora_do_escopo": False},
            "assinante": {
                "proposta": {
                    "tipo": "pedido_cesta", "tamanho": "media", "modo": "selecionavel",
                    "produtos": [{"produto_id": n, "quantidade": 1} for n in nomes],
                },
                "mensagem": "Confira.", "pergunta": None,
            },
            "qa": {"status": "aprovado", "problemas": [], "duvidas": []},
        }
        return contrato.model_validate(respostas[papel])

    resultado = analisar_agentes(mensagem, "assinante", catalogo, [], chamar_agente=chamar, modo="openrouter")
    assert auditoria_capturada["erros_validacao"]
    assert resultado["proposta"] is None
    assert resultado["qa"]["status"] == "bloqueado"

    resultado_simulado = simulado.analisar(mensagem, "assinante", catalogo, [])
    assert resultado_simulado["status"] == "esclarecimento"
    assert resultado_simulado["qa"]["status"] == "esclarecimento"
    assert resultado_simulado["qa"]["problemas"]


def test_perfil_desconhecido_nao_chama_modelo():
    def nao_chamar(*args):
        pytest.fail("Perfil inválido não deve chamar o provedor.")

    with pytest.raises(ValueError, match="Perfil"):
        analisar_agentes("Uma cesta", "administrador", [], [],
                         chamar_agente=nao_chamar, modo="openrouter")
