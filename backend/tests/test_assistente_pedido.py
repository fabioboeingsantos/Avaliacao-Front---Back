"""Verifica a rota de proposta sem criar pedidos automaticamente."""

from ia.pedido_cesta import ResultadoPropostaCesta
from ia.provedores.contrato import AssistenteIndisponivel
from modelos.produto import Produto
from tests.conftest import SessaoDeTeste, fazer_login


def proposta_ficticia():
    """Montar uma resposta falsa para comprovar a prévia antes da confirmação."""
    return ResultadoPropostaCesta.model_validate({
        "modo": "simulado", "agente": "assinante", "status": "proposta",
        "proposta": {
            "tipo": "pedido_cesta", "tamanho": "pequena", "modo": "selecionavel",
            "produtos": [{"produto_id": "tomate", "quantidade": 1}],
            "produtos_excluidos": [],
        },
        "qa": {"status": "aprovado", "problemas": [], "duvidas": []},
        "mensagem": "Confira a proposta antes de continuar.",
    })


def test_post_devolve_proposta_sem_gravar_pedido(cliente, monkeypatch):
    """Garantir que a rota só devolve a sugestão até a pessoa confirmar depois."""
    fazer_login(cliente, "aline", "aline123")
    quantidade_antes = len(cliente.get("/cestas").json())
    monkeypatch.setattr("rotas.assistente.propor_cesta", lambda _mensagem, _sessao: proposta_ficticia())

    resposta = cliente.post("/assistente/pedido", json={"mensagem": "Quero uma cesta fictícia."})

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "proposta"
    assert len(cliente.get("/cestas").json()) == quantidade_antes


def test_post_de_proposta_restringe_o_perfil_produtor(cliente):
    """Impedir que o endpoint de montagem seja usado pelo perfil produtor."""
    fazer_login(cliente, "vanderlei", "vanderlei123")

    resposta = cliente.post("/assistente/pedido", json={"mensagem": "Pedido fictício."})

    assert resposta.status_code == 403


def test_post_de_proposta_simulada_aceita_produtos_do_catalogo(cliente):
    fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post(
        "/assistente/pedido", json={"mensagem": "Quero uma cesta pequena com 2 alfaces"},
    )
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "proposta"
    produto = resposta.json()["proposta"]["produtos"][0]
    assert produto["produto_id"] == "alface"
    assert produto["quantidade"] == 2


def test_ajuste_por_conversa_preserva_cesta_e_recalcula_itens(cliente):
    fazer_login(cliente, "aline", "aline123")
    antes = cliente.get("/cestas").json()
    original = cliente.post("/assistente/pedido", json={
        "mensagem": "Quero uma cesta média com dois tomates, cenoura e couve.",
    }).json()["proposta"]
    assert {item["produto_id"]: item["quantidade"] for item in original["produtos"]} == {
        "tomate": 2, "cenoura": 1, "couve": 1,
    }
    ajuste = cliente.post("/assistente/pedido", json={
        "mensagem": "Só um tomate. E troca a couve por alface.", "rascunho": original,
    })
    assert ajuste.status_code == 200
    proposta = ajuste.json()["proposta"]
    assert proposta["tamanho"] == "media"
    assert {item["produto_id"]: item["quantidade"] for item in proposta["produtos"]} == {
        "tomate": 1, "cenoura": 1, "alface": 1,
    }
    invalido = cliente.post("/assistente/pedido", json={
        "mensagem": "Deixa 11 tomates", "rascunho": proposta,
    }).json()
    assert invalido["status"] == "esclarecimento"
    assert invalido["proposta"] is None
    assert cliente.get("/cestas").json() == antes


def test_substituicao_revalida_estoque_e_preserva_os_demais_itens(cliente):
    with SessaoDeTeste() as sessao:
        sessao.get(Produto, "alface").estoque = 0
        sessao.commit()
    fazer_login(cliente, "aline", "aline123")
    pedidos_antes = cliente.get("/cestas").json()
    resposta = cliente.post("/assistente/pedido", json={
        "mensagem": "Quero uma cesta pequena com tomate e 2 alfaces",
    })
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["proposta"] is None
    assert [produto["id"] for produto in dados["falta"]["alternativas"]] == ["couve"]
    escolha = {"rascunho": dados["rascunho"], "produto_id": "alface", "substituto_id": "couve"}
    previa = cliente.post("/assistente/pedido/substituicao", json=escolha).json()
    assert {item["produto_id"]: item["quantidade"] for item in previa["proposta"]["produtos"]} == {
        "tomate": 1, "couve": 2,
    }
    assert {produto["id"] for produto in previa["precos"]} == {"tomate", "couve"}

    with SessaoDeTeste() as sessao:
        sessao.get(Produto, "couve").estoque = 1
        sessao.commit()
    atualizada = cliente.post("/assistente/pedido/substituicao", json=escolha).json()
    assert atualizada["proposta"] is None
    assert atualizada["falta"]["alternativas"] == []

    sem_alface = cliente.post("/assistente/pedido/substituicao", json={**escolha, "substituto_id": None}).json()
    assert sem_alface["proposta"]["produtos"] == [{"produto_id": "tomate", "quantidade": 1}]
    assert cliente.get("/cestas").json() == pedidos_antes


def test_post_de_proposta_responde_503_com_frase_segura(cliente, monkeypatch):
    """Informar indisponibilidade sem repassar detalhes internos do provedor."""
    fazer_login(cliente, "aline", "aline123")

    def indisponivel(_mensagem, _sessao):
        raise AssistenteIndisponivel("erro interno com dado privado")

    monkeypatch.setattr("rotas.assistente.propor_cesta", indisponivel)
    resposta = cliente.post("/assistente/pedido", json={"mensagem": "Pedido fictício."})

    assert resposta.status_code == 503
    assert "monte a cesta manualmente" in resposta.json()["detail"]
    assert "privado" not in resposta.json()["detail"]
