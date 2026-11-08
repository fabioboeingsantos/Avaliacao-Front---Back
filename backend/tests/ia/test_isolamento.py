"""O contexto simulado deve respeitar o mesmo acesso do provedor real."""

from ia.provedores import simulado
from ..conftest import fazer_login


def test_simulado_recebe_somente_cestas_da_conta(cliente, monkeypatch):
    original = simulado.analisar
    capturas = []

    def analisar(mensagem, perfil, catalogo, cestas, historico=None):
        capturas.extend(cestas)
        return original(mensagem, perfil, catalogo, cestas, historico=historico)

    monkeypatch.setenv("ASSISTENTE_MODO", "simulado")
    monkeypatch.setattr(simulado, "analisar", analisar)
    fazer_login(cliente, "aline", "aline123")
    autorizadas = cliente.get("/cestas").json()
    resposta = cliente.post("/assistente/analisar", json={"mensagem": "Quero cesta"})
    assert resposta.status_code == 200
    assert [c["id"] for c in capturas] == [c["id"] for c in autorizadas]
    assert all("assinante" not in c and "preco" not in c for c in capturas)


def test_simulado_respeita_exclusao(cliente, monkeypatch):
    monkeypatch.setenv("ASSISTENTE_MODO", "simulado")
    fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post("/assistente/analisar", json={
        "mensagem": "Cesta média com tomate sem cebola",
    })
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["modo"] == "simulado"
    assert [p["produto_id"] for p in dados["proposta"]["produtos"]] == ["tomate"]
    assert dados["proposta"]["produtos_excluidos"] == ["cebola"]
