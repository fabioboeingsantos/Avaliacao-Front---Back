"""Verifica a rota de proposta sem criar pedidos automaticamente."""

from ia.pedido_cesta import ResultadoPropostaCesta
from ia.provedores.contrato import AssistenteIndisponivel
from tests.conftest import fazer_login


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


def test_post_de_proposta_responde_503_com_frase_segura(cliente, monkeypatch):
    """Informar indisponibilidade sem repassar detalhes internos do provedor."""
    fazer_login(cliente, "aline", "aline123")

    def indisponivel(_mensagem, _sessao):
        raise AssistenteIndisponivel("erro interno com dado privado")

    monkeypatch.setattr("rotas.assistente.propor_cesta", indisponivel)
    resposta = cliente.post("/assistente/pedido", json={"mensagem": "Pedido fictício."})

    assert resposta.status_code == 503
    assert "continue" in resposta.json()["detail"]
    assert "privado" not in resposta.json()["detail"]
