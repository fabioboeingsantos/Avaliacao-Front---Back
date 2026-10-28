def test_health_retorna_status_ok(cliente):
    resposta = cliente.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_saude_preserva_resposta_existente(cliente):
    resposta = cliente.get("/saude")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "status": "ok",
        "mensagem": "Cesta do Vale API online",
    }
