"""Consultas operacionais não podem inventar dados nem executar gravações."""

import pytest

from ia import consultas
from ia.contratos import PropostaAgente
from ia.validacao import validar_proposta
from ..conftest import fazer_login


@pytest.fixture
def dados_consulta(monkeypatch):
    catalogo = [
        {"id": "tomate", "nome": "Tomate", "estoque": 17},
        {"id": "alface", "nome": "Alface", "estoque": 0},
        {"id": "pimentao", "nome": "Pimentão", "estoque": 4},
    ]
    cestas = [
        {"id": indice, "situacao": situacao, "separacao_concluida_em": None,
         "produtos": [{"id": "tomate", "quantidade": 2}], "separacoes": []}
        for indice, situacao in enumerate(consultas.SITUACOES, start=1)
    ]
    monkeypatch.setattr(consultas, "carregar_catalogo", lambda sessao: catalogo)
    monkeypatch.setattr(consultas, "carregar_cestas", lambda sessao, perfil, usuario_id, limite: cestas)
    return catalogo, cestas


def perguntar(texto, perfil="produtor"):
    return consultas.responder(texto, perfil, None, 1, "simulado")


@pytest.mark.parametrize("texto,esperado,ausente", [
    ("Flora me diga quantos tomates eu tenho no estoque", "Tomate: 17", "Alface:"),
    ("Quantos tomates tenho?", "Tomate: 17", "Alface:"),
    ("Qual o estoque de pimentões?", "Pimentão: 4", "Tomate:"),
    ("Mostre o estoque completo", "Alface: 0", "produto inexistente"),
    ("Flora mostre meu estoque", "Tomate: 17", "produto inexistente"),
    ("Quais produtos têm estoque baixo?", "Pimentão: 4", "Tomate:"),
    ("Quais produtos estão esgotados?", "Alface: 0", "Tomate:"),
])
def test_estoque_real_e_filtros(dados_consulta, texto, esperado, ausente):
    resultado = perguntar(texto)
    assert resultado["status"] == "resposta"
    assert resultado["proposta"] is None
    assert esperado in resultado["mensagem"]
    assert ausente not in resultado["mensagem"]


def test_produto_desconhecido_pede_esclarecimento(dados_consulta):
    resultado = perguntar("Qual o estoque de bananas?")
    assert resultado["status"] == "esclarecimento"
    assert "Tomate: 17" not in resultado["mensagem"]


@pytest.mark.parametrize("texto,esperados,ausentes", [
    ("Mostre todas as entregas pendentes", ["#0003", "#0004", "#0005"], ["#0001", "#0006", "#0007"]),
    ("Quais pedidos estão em separação?", ["#0002"], ["#0001", "#0003"]),
    ("Mostre os pedidos entregues", ["#0006"], ["#0003", "#0004"]),
    ("Mostre os pedidos não entregues", ["#0001", "#0002", "#0004"], ["#0006", "#0007"]),
    ("Mostre os pedidos não cancelados", ["#0001", "#0006"], ["#0007"]),
    ("Quais são as pendências?", ["#0001", "#0002", "#0003", "#0004", "#0005"], ["#0006", "#0007"]),
])
def test_filtros_de_situacao(dados_consulta, texto, esperados, ausentes):
    mensagem = perguntar(texto)["mensagem"]
    assert all(numero in mensagem for numero in esperados)
    assert all(numero not in mensagem for numero in ausentes)


def test_relatorio_conta_todos_e_indica_limite_de_detalhes(dados_consulta, monkeypatch):
    cestas = [{**dados_consulta[1][0], "id": i} for i in range(1, 36)]
    def carregar(sessao, perfil, usuario_id, limite):
        assert limite is None
        return cestas
    monkeypatch.setattr(consultas, "carregar_cestas", carregar)
    mensagem = perguntar("Resumo do sistema")["mensagem"]
    assert "35 pedidos" in mensagem
    assert "Pendente: 35" in mensagem
    assert "Exibindo 30 de 35" in mensagem


@pytest.mark.parametrize("texto", ["Já separei o pedido 12", "Abra a cesta 12", "Quero uma cesta pequena com tomate"])
def test_comandos_continuam_no_fluxo_de_confirmacao(texto):
    assert perguntar(texto) is None


def test_api_exige_login(cliente):
    resposta = cliente.post("/assistente/analisar", json={"mensagem": "Estoque completo"})
    assert resposta.status_code == 401


def test_assinante_recebe_catalogo_sem_quantidades_nem_pedido_de_outra_conta(cliente):
    fazer_login(cliente, "aline", "aline123")
    estoque = cliente.post("/assistente/analisar", json={"mensagem": "Estoque completo"}).json()
    assert "Catálogo disponível" in estoque["mensagem"]
    assert "unidades" not in estoque["mensagem"]
    assert "20" not in estoque["mensagem"]
    resumo = cliente.post("/assistente/analisar", json={"mensagem": "Quantos pedidos eu tenho?"}).json()
    assert "1 pedido" in resumo["mensagem"]
    assert "#0002" not in resumo["mensagem"]
    detalhe = cliente.post("/assistente/analisar", json={"mensagem": "Situação do pedido 2"}).json()
    assert "Não encontrei" in detalhe["mensagem"]


def test_consultas_api_usam_banco_sem_gravar_ou_chamar_modelo(cliente, monkeypatch):
    fazer_login(cliente, "vanderlei", "vanderlei123")
    assert cliente.put("/produtos/tomate/estoque", json={"quantidade": 37}).status_code == 200
    estoque_antes = cliente.get("/produtos").json()
    pedidos_antes = cliente.get("/cestas").json()
    monkeypatch.setenv("ASSISTENTE_MODO", "openrouter")
    from ia.provedores import openrouter
    def proibido(*args, **kwargs):
        pytest.fail("Consultas de leitura não devem chamar um modelo externo")
    monkeypatch.setattr(openrouter, "chamar_agente", proibido)
    for texto in ["Quantos tomates tenho no estoque?", "Resumo do sistema", "Mostre as entregas pendentes"]:
        resposta = cliente.post("/assistente/analisar", json={"mensagem": texto})
        assert resposta.status_code == 200
        assert resposta.json()["status"] == "resposta"
        assert resposta.json()["proposta"] is None
        if "tomates" in texto:
            assert "Tomate: 37" in resposta.json()["mensagem"]
    assert cliente.get("/produtos").json() == estoque_antes
    assert cliente.get("/cestas").json() == pedidos_antes


def test_declarar_separacao_exige_confirmacao_e_conclui_na_api(cliente):
    fazer_login(cliente, "vanderlei", "vanderlei123")
    resposta = cliente.post("/assistente/analisar", json={"mensagem": "Já separei o pedido 1"})
    dados = resposta.json()
    assert resposta.status_code == 200
    assert dados["status"] == "proposta"
    assert dados["proposta"]["concluir_separacao"] is True
    assert cliente.get("/cestas/1").json()["situacao"] == "Pendente"
    confirmacao = cliente.put("/cestas/1/separacoes", json={"produtos": dados["proposta"]["produtos"]})
    assert confirmacao.status_code == 200
    assert confirmacao.json()["situacao"] == "Preparado para envio"
    assert confirmacao.json()["separacao_concluida_em"] is not None
    repetida = cliente.post("/assistente/analisar", json={"mensagem": "Já separei o pedido 1"}).json()
    assert repetida["qa"]["status"] == "bloqueado"


@pytest.mark.parametrize("produtos,aprovado", [
    ([{"produto_id": "tomate", "quantidade": 2}, {"produto_id": "alface", "quantidade": 1}], True),
    ([{"produto_id": "tomate", "quantidade": 2}], False),
    ([{"produto_id": "tomate", "quantidade": 3}, {"produto_id": "alface", "quantidade": 1}], False),
    ([{"produto_id": "tomate", "quantidade": 2}, {"produto_id": "tomate", "quantidade": 2}], False),
])
def test_conclusao_com_progresso_anterior_exige_composicao_exata(produtos, aprovado):
    cesta = {"id": 1, "situacao": "Em separação", "separacao_concluida_em": None,
             "produtos": [{"id": "tomate", "quantidade": 2}, {"id": "alface", "quantidade": 1}],
             "separacoes": [{"produto_id": "tomate", "quantidade": 1}]}
    proposta = PropostaAgente(tipo="separacao", cesta_id=1, concluir_separacao=True, produtos=produtos)
    catalogo = [{"id": "tomate", "estoque": 10}, {"id": "alface", "estoque": 10}]
    erros = validar_proposta(proposta, "produtor", catalogo, [cesta])
    assert (not erros) == aprovado
