"""Testes de propriedade das cestas e permissoes por perfil."""

from .conftest import fazer_login


def test_assinante_ve_somente_as_proprias_cestas(cliente):
    """A consulta do assinante e filtrada pelo usuario do token."""

    token = fazer_login(cliente, "aline", "aline123")
    resposta = cliente.get("/cestas", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["assinante"] == "aline"


def test_assinante_nao_acessa_cesta_de_outro_usuario(cliente):
    """Um id valido de outra conta se comporta como nao encontrado."""

    token_produtor = fazer_login(cliente, "vanderlei", "vanderlei123")
    cestas = cliente.get(
        "/cestas",
        headers={"Authorization": f"Bearer {token_produtor}"},
    ).json()
    cesta_de_outro_usuario = next(cesta for cesta in cestas if cesta["assinante"] == "vanderlei")

    token = fazer_login(cliente, "aline", "aline123")
    resposta = cliente.get(
        f"/cestas/{cesta_de_outro_usuario['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 404


def test_assinante_nao_pode_registrar_separacao(cliente):
    """A separacao e uma operacao exclusiva do perfil produtor."""

    token = fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post(
        "/cestas/1/separacoes",
        headers={"Authorization": f"Bearer {token}"},
        json={"produto_id": "alface", "quantidade": 1},
    )

    assert resposta.status_code == 403


def test_produtor_pode_registrar_separacao(cliente):
    """O produtor autenticado pode atualizar uma cesta existente."""

    token = fazer_login(cliente, "vanderlei", "vanderlei123")
    resposta = cliente.post(
        "/cestas/1/separacoes",
        headers={"Authorization": f"Bearer {token}"},
        json={"produto_id": "alface", "quantidade": 1},
    )

    assert resposta.status_code == 200
    assert resposta.json()["separacoes"][0]["quantidade"] == 1


def test_criacao_usa_o_usuario_do_token(cliente):
    """O cliente nao consegue criar uma cesta em nome de outra conta."""

    token = fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post(
        "/cestas",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "assinante": "vanderlei",
            "usuario_id": 2,
            "tamanho": "pequena",
            "modo": "pronta",
            "produtos": [{"id": "alface", "nome": "Alface", "quantidade": 1}],
        },
    )

    assert resposta.status_code == 201
    assert resposta.json()["assinante"] == "aline"
