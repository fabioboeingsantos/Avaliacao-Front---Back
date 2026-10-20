"""Testes de senha, login e validacao dos tokens."""

from datetime import datetime, timedelta, timezone

import jwt

from configuracao import obter_chave_jwt
from servicos.senhas import criar_hash_de_senha, senha_confere

from .conftest import fazer_login


def test_senha_e_protegida_e_validada(cliente):
    """A senha nao volta em texto puro e somente o valor correto e aceito."""

    senha_hash = criar_hash_de_senha("senha-segura")

    assert senha_hash.startswith("$argon2")
    assert senha_confere("senha-segura", senha_hash)
    assert not senha_confere("senha-errada", senha_hash)


def test_login_devolve_jwt_com_identidade_e_perfil(cliente):
    """O login entrega a sessao em cookie HttpOnly com os dados corretos."""

    resposta = cliente.post(
        "/autenticacao/login",
        json={"usuario": "aline", "senha": "aline123"},
    )
    corpo = resposta.json()
    token = cliente.cookies.get("access_token")
    dados_token = jwt.decode(token, obter_chave_jwt(), algorithms=["HS256"])

    assert resposta.status_code == 200
    assert token
    assert "access_token" not in corpo
    assert dados_token["sub"] == "aline"
    assert dados_token["perfil"] == "assinante"
    assert "senha" not in corpo


def test_login_rejeita_senha_incorreta(cliente):
    """Credenciais invalidas nao recebem token."""

    resposta = cliente.post(
        "/autenticacao/login",
        json={"usuario": "aline", "senha": "incorreta"},
    )

    assert resposta.status_code == 401
    assert "access_token" not in resposta.json()


def test_rota_rejeita_token_invalido(cliente):
    """Uma assinatura desconhecida nao pode abrir uma rota protegida."""

    resposta = cliente.get("/cestas", headers={"Authorization": "Bearer token-invalido"})

    assert resposta.status_code == 401


def test_rota_rejeita_token_expirado(cliente):
    """Tokens vencidos deixam de autorizar novas chamadas."""

    expirado = jwt.encode(
        {
            "sub": "aline",
            "perfil": "assinante",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        obter_chave_jwt(),
        algorithm="HS256",
    )
    resposta = cliente.get("/cestas", headers={"Authorization": f"Bearer {expirado}"})

    assert resposta.status_code == 401


def test_rota_exige_token(cliente):
    """Sem o cabecalho Bearer a API nao entrega cestas."""

    resposta = cliente.get("/cestas")

    assert resposta.status_code == 401


def test_usuario_eu_exige_token(cliente):
    """A rota de identidade recusa chamadas sem autenticacao."""

    resposta = cliente.get("/usuarios/eu")

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Not authenticated"


def test_usuario_eu_retorna_usuario_autenticado(cliente):
    """A rota de identidade devolve a conta associada ao token."""

    token = fazer_login(cliente, "aline", "aline123")
    resposta = cliente.get("/usuarios/eu", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 200
    assert resposta.json()["usuario"] == "aline"
    assert resposta.json()["perfil"] == "assinante"
