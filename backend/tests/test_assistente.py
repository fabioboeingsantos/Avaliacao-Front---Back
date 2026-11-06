"""Contrato, isolamento de contas e falhas dos agentes sem consumir a API."""

import json

import httpx
import pytest

from modelos.cesta import Cesta
from servicos import provedor_kimi
from .conftest import SessaoDeTeste, fazer_login


def configurar_kimi(monkeypatch, respostas, capturas):
    monkeypatch.setenv("ASSISTENTE_MODO", "kimi")
    monkeypatch.setenv("KIMI_API_KEY", "chave-ficticia-exclusiva-teste")
    cliente_original = httpx.Client

    def responder(requisicao):
        capturas.append(json.loads(requisicao.content))
        valor = respostas.pop(0)
        if isinstance(valor, int):
            return httpx.Response(valor, json={"error": "detalhe privado do provedor"})
        return httpx.Response(200, json={"choices": [{
            "finish_reason": "stop", "message": {"content": json.dumps(valor)},
        }]})

    monkeypatch.setattr(provedor_kimi.httpx, "Client", lambda **opcoes: cliente_original(
        transport=httpx.MockTransport(responder), **opcoes,
    ))


def respostas_padrao(qa=None, proposta=None):
    return [
        {"intencao": "Montar cesta", "fora_do_escopo": False},
        {"mensagem": "Confira sua cesta.", "pergunta": None, "proposta": proposta or {
            "tipo": "pedido_cesta", "tamanho": "media", "produtos": [{"produto_id": "tomate", "quantidade": 2}],
        }},
        qa or {"status": "aprovado", "problemas": [], "duvidas": []},
    ]


def test_exige_login(cliente):
    assert cliente.post("/assistente/analisar", json={"mensagem": "Uma cesta média"}).status_code == 401


def test_tres_agentes_e_historico_privado(cliente, monkeypatch):
    capturas = []
    configurar_kimi(monkeypatch, respostas_padrao(), capturas)
    fazer_login(cliente, "aline", "aline123")
    antes = cliente.get("/cestas").json()
    resposta = cliente.post("/assistente/analisar", json={"mensagem": "Cesta média com 2 tomates"})
    assert resposta.status_code == 200
    assert resposta.json()["modo"] == "kimi"
    assert resposta.json()["qa"]["status"] == "aprovado"
    assert len(capturas) == 3
    for captura in capturas:
        contexto = json.loads(captura["messages"][1]["content"])
        assert [c["id"] for c in contexto["cestas_autorizadas"]] == [antes[0]["id"]]
        assert "preco" not in captura["messages"][1]["content"]
        assert "senha" not in captura["messages"][1]["content"]
    assert cliente.get("/cestas").json() == antes


def test_qa_reprovado_oculta_proposta(cliente, monkeypatch):
    configurar_kimi(monkeypatch, respostas_padrao(qa={"status": "esclarecimento", "duvidas": ["Qual tamanho você quer?"], "problemas": []}), [])
    fazer_login(cliente, "aline", "aline123")
    dados = cliente.post("/assistente/analisar", json={"mensagem": "Quero tomates"}).json()
    assert dados["status"] == "esclarecimento"
    assert dados["proposta"] is None
    assert dados["mensagem"] == "Qual tamanho você quer?"


@pytest.mark.parametrize("produto", ["inventado", "tomate"])
def test_regras_locais_prevalecem_sobre_qa(cliente, monkeypatch, produto):
    proposta = {"tipo": "pedido_cesta", "tamanho": "pequena", "produtos": [
        {"produto_id": produto, "quantidade": 1},
    ], "produtos_excluidos": [produto]}
    configurar_kimi(monkeypatch, respostas_padrao(proposta=proposta), [])
    fazer_login(cliente, "aline", "aline123")
    dados = cliente.post("/assistente/analisar", json={"mensagem": "Sem tomate"}).json()
    assert dados["qa"]["status"] == "bloqueado"
    assert dados["proposta"] is None


def test_produtor_nao_separa_cesta_enviada(cliente, monkeypatch):
    with SessaoDeTeste() as sessao:
        cesta = sessao.get(Cesta, 1)
        cesta.situacao = "Enviado"
        sessao.commit()
    proposta = {"tipo": "separacao", "cesta_id": 1, "produtos": [{"produto_id": "alface", "quantidade": 1}]}
    configurar_kimi(monkeypatch, respostas_padrao(proposta=proposta), [])
    fazer_login(cliente, "vanderlei", "vanderlei123")
    dados = cliente.post("/assistente/analisar", json={"mensagem": "Separe 1 alface na cesta 1"}).json()
    assert dados["qa"]["status"] == "bloqueado"
    assert dados["proposta"] is None


@pytest.mark.parametrize("codigo", [401, 429, 500])
def test_falha_provedor_nao_vaza_detalhes(cliente, monkeypatch, codigo):
    configurar_kimi(monkeypatch, [codigo], [])
    fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post("/assistente/analisar", json={"mensagem": "Cesta média"})
    assert resposta.status_code == 503
    assert "detalhe privado" not in resposta.text
    assert "chave-ficticia" not in resposta.text


def test_sem_chave_falha_sem_chamada(cliente, monkeypatch):
    monkeypatch.setenv("ASSISTENTE_MODO", "kimi")
    monkeypatch.setenv("KIMI_API_KEY", "")
    fazer_login(cliente, "aline", "aline123")
    assert cliente.post("/assistente/analisar", json={"mensagem": "Uma cesta"}).status_code == 503


def test_json_invalido_nao_libera_proposta(cliente, monkeypatch):
    configurar_kimi(monkeypatch, [{"campos": "inesperados"}], [])
    fazer_login(cliente, "aline", "aline123")
    assert cliente.post("/assistente/analisar", json={"mensagem": "Uma cesta"}).status_code == 503


def test_nao_aceita_perfil_do_frontend(cliente):
    fazer_login(cliente, "aline", "aline123")
    assert cliente.post("/assistente/analisar", json={"mensagem": "Uma cesta", "perfil": "produtor"}).status_code == 422


def test_simulado_respeita_exclusao_sem_chamar_provedor(cliente, monkeypatch):
    def nao_chamar(*args, **kwargs):
        pytest.fail("Simulação não pode acessar provedor externo")
    monkeypatch.setattr(provedor_kimi, "chamar_agente", nao_chamar)
    fazer_login(cliente, "aline", "aline123")
    dados = cliente.post("/assistente/analisar", json={"mensagem": "Cesta média com tomate sem cebola"}).json()
    assert dados["modo"] == "simulado"
    assert [item["produto_id"] for item in dados["proposta"]["produtos"]] == ["tomate"]
    assert dados["proposta"]["produtos_excluidos"] == ["cebola"]


def test_cesta_pronta_divergente_nao_e_aprovada(cliente, monkeypatch):
    configurar_kimi(monkeypatch, respostas_padrao(proposta={
        "tipo": "pedido_cesta", "tamanho": "pequena", "modo": "pronta",
        "produtos": [{"produto_id": "tomate", "quantidade": 1}],
    }), [])
    fazer_login(cliente, "aline", "aline123")
    dados = cliente.post("/assistente/analisar", json={"mensagem": "Quero a cesta pronta pequena"}).json()
    assert dados["qa"]["status"] == "bloqueado"
    assert dados["proposta"] is None


def test_esclarecimento_simulado_tem_so_uma_pergunta(cliente):
    fazer_login(cliente, "aline", "aline123")
    dados = cliente.post("/assistente/analisar", json={"mensagem": "Quero cesta"}).json()
    assert len(dados["qa"]["duvidas"]) == 1
