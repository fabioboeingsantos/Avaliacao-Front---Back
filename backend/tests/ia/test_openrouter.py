"""Integração OpenRouter com transporte local, sem chave real ou consumo de cota."""

import json

import httpx
import pytest

from ia.contratos import InterpretacaoAgente
from ia.provedores import openrouter as provedor_openrouter
from ia.provedores.contrato import AssistenteIndisponivel
from ..conftest import fazer_login


def respostas_padrao(qa=None, proposta=None):
    return [
        {"intencao": "Montar cesta", "fora_do_escopo": False},
        {"mensagem": "Confira sua cesta.", "pergunta": None, "proposta": proposta or {
            "tipo": "pedido_cesta", "tamanho": "media", "produtos": [{"produto_id": "tomate", "quantidade": 2}],
        }},
        qa or {"status": "aprovado", "problemas": [], "duvidas": []},
    ]


def preparar(monkeypatch, respostas):
    monkeypatch.setenv("ASSISTENTE_MODO", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia-openrouter")
    monkeypatch.setenv("OPENROUTER_MODEL", "openrouter/free")
    monkeypatch.setenv("IA_MODELO_PADRAO", "")
    for papel in ("INTERPRETE", "ASSINANTE", "PRODUTOR", "QA"):
        monkeypatch.setenv(f"OPENROUTER_MODEL_{papel}", "")
        monkeypatch.setenv(f"IA_MODELO_{papel}", "")
    capturas = []
    cliente_original = httpx.Client

    def responder(requisicao):
        assert str(requisicao.url) == "https://openrouter.ai/api/v1/chat/completions"
        capturas.append(json.loads(requisicao.content))
        valor = respostas.pop(0)
        if isinstance(valor, int):
            return httpx.Response(valor, json={"error": {"message": "segredo-do-provedor"}})
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(valor)}}]})

    monkeypatch.setattr(provedor_openrouter.httpx, "Client", lambda **opcoes: cliente_original(
        transport=httpx.MockTransport(responder), **opcoes,
    ))
    return capturas


def test_tres_chamadas_gratuitas_e_isolamento(cliente, monkeypatch):
    capturas = preparar(monkeypatch, respostas_padrao())
    fazer_login(cliente, "aline", "aline123")
    antes = cliente.get("/cestas").json()
    resposta = cliente.post("/assistente/analisar", json={"mensagem": "Cesta média com 2 tomates"})
    assert resposta.status_code == 200
    assert resposta.json()["modo"] == "openrouter"
    assert resposta.json()["qa"]["status"] == "aprovado"
    assert len(capturas) == 3
    for corpo in capturas:
        assert corpo["model"] == "openrouter/free"
        assert corpo["provider"] == {"require_parameters": True, "max_price": {"prompt": 0, "completion": 0}}
        assert "max_tokens" in corpo and "max_completion_tokens" not in corpo
        assert corpo["reasoning"] == {"enabled": False}
        formato = corpo["response_format"]
        assert formato["type"] == "json_schema"
        assert formato["json_schema"]["strict"] is True
        schema = formato["json_schema"]["schema"]
        assert set(schema["required"]) == set(schema["properties"])
        contexto = json.loads(corpo["messages"][1]["content"])
        assert contexto["operacoes_permitidas"] == ["consulta_cestas", "pedido_cesta"]
        assert [c["id"] for c in contexto["cestas_autorizadas"]] == [antes[0]["id"]]
    assert cliente.get("/cestas").json() == antes


def test_modelos_separados_por_agente(cliente, monkeypatch):
    capturas = preparar(monkeypatch, respostas_padrao())
    monkeypatch.setenv("IA_MODELO_PADRAO", "exemplo/padrao:free")
    monkeypatch.setenv("IA_MODELO_INTERPRETE", "exemplo/interprete:free")
    monkeypatch.setenv("OPENROUTER_MODEL_QA", "exemplo/qa-legado:free")
    monkeypatch.setenv("IA_MODELO_QA", "exemplo/qa:free")
    fazer_login(cliente, "aline", "aline123")
    assert cliente.post("/assistente/analisar", json={"mensagem": "Uma cesta média"}).status_code == 200
    assert [c["model"] for c in capturas] == ["exemplo/interprete:free", "exemplo/padrao:free", "exemplo/qa:free"]


def test_contexto_de_conversa_e_disponibilidade_chegam_aos_agentes(cliente, monkeypatch):
    capturas = preparar(monkeypatch, respostas_padrao())
    fazer_login(cliente, "aline", "aline123")
    historico = [{"papel": "usuario", "texto": "Quero uma cesta com 2 tomates"},
                 {"papel": "flora", "texto": "Qual tamanho você prefere?"}]
    resposta = cliente.post('/assistente/analisar', json={"mensagem": "média", "historico": historico})
    assert resposta.status_code == 200
    for corpo in capturas:
        contexto = json.loads(corpo['messages'][1]['content'])
        assert contexto['historico_conversa'] == historico
        assert all(p['estoque'] > 0 for p in contexto['catalogo_disponivel'])
        assert all(p['categoria'] in {'frutas', 'verduras', 'legumes'} for p in contexto['catalogo_disponivel'])


def test_agente_produtor(cliente, monkeypatch):
    capturas = preparar(monkeypatch, respostas_padrao(proposta={
        "tipo": "separacao", "cesta_id": 1, "produtos": [{"produto_id": "alface", "quantidade": 1}],
    }))
    monkeypatch.setenv("OPENROUTER_MODEL_PRODUTOR", "exemplo/produtor:free")
    fazer_login(cliente, "vanderlei", "vanderlei123")
    dados = cliente.post("/assistente/analisar", json={"mensagem": "Separe 1 alface na cesta 1"}).json()
    assert dados["qa"]["status"] == "aprovado"
    assert capturas[1]["model"] == "exemplo/produtor:free"
    contexto_qa = json.loads(capturas[2]["messages"][1]["content"])
    assert contexto_qa["operacoes_permitidas"] == ["consulta_cestas", "separacao"]


def test_qa_reprovado_bloqueia(cliente, monkeypatch):
    preparar(monkeypatch, respostas_padrao(qa={"status": "bloqueado", "problemas": ["Produto divergente"], "duvidas": []}))
    fazer_login(cliente, "aline", "aline123")
    dados = cliente.post("/assistente/analisar", json={"mensagem": "Uma cesta"}).json()
    assert dados["proposta"] is None
    assert dados["qa"]["status"] == "bloqueado"


@pytest.mark.parametrize("codigo", [401, 402, 403, 404, 429, 500, 502, 503])
def test_falhas_sem_vazamento_ou_retry(cliente, monkeypatch, codigo):
    capturas = preparar(monkeypatch, [codigo])
    fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post("/assistente/analisar", json={"mensagem": "Uma cesta"})
    assert resposta.status_code == 503
    assert "segredo-do-provedor" not in resposta.text
    assert "chave-ficticia" not in resposta.text
    assert len(capturas) == 1


def test_sem_chave_nao_chama_provedor(cliente, monkeypatch):
    capturas = preparar(monkeypatch, [])
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    fazer_login(cliente, "aline", "aline123")
    assert cliente.post("/assistente/analisar", json={"mensagem": "Uma cesta"}).status_code == 503
    assert not capturas


def test_modelo_pago_bloqueado_sem_chamada(monkeypatch):
    monkeypatch.setenv("IA_MODELO_PADRAO", "")
    monkeypatch.setenv("IA_MODELO_INTERPRETE", "")
    monkeypatch.setenv("OPENROUTER_MODEL_INTERPRETE", "")
    capturas = preparar(monkeypatch, [])
    monkeypatch.setenv("OPENROUTER_MODEL", "exemplo/modelo-pago")
    with pytest.raises(AssistenteIndisponivel, match=":free"):
        provedor_openrouter.chamar_agente("interprete", "Teste", {}, InterpretacaoAgente)
    assert not capturas


def test_json_incompativel_bloqueia(cliente, monkeypatch):
    preparar(monkeypatch, [{"campos": "inesperados"}])
    fazer_login(cliente, "aline", "aline123")
    assert cliente.post("/assistente/analisar", json={"mensagem": "Uma cesta"}).status_code == 503


def test_schema_estrito_preserva_nulos_e_requer_objetos_aninhados():
    from ia.contratos import RespostaEspecialista
    schema = provedor_openrouter._schema_estrito(RespostaEspecialista.model_json_schema())
    assert set(schema["required"]) == {"proposta", "pergunta", "mensagem"}
    assert {"type": "null"} in schema["properties"]["pergunta"]["anyOf"]
    for definicao in schema["$defs"].values():
        if definicao.get("type") == "object":
            assert definicao["additionalProperties"] is False
            assert set(definicao["required"]) == set(definicao["properties"])
