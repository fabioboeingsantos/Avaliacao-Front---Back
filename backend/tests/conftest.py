"""Fixtures compartilhadas pelos testes da API."""

import os
from collections.abc import Generator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


# Os testes nunca devem depender da chave ou do banco configurados no .env local.
os.environ["JWT_SECRET_KEY"] = "chave-exclusiva-dos-testes-com-mais-de-32"
os.environ["JWT_ALGORITHM"] = "HS256"
# Mantém os testes alinhados à validade padrão da sessão.
os.environ["JWT_EXPIRATION_MINUTES"] = "1440"

from banco import Base, obter_sessao  # noqa: E402
from limites_autenticacao import limitador  # noqa: E402
from main import app  # noqa: E402
from modelos.cesta import Cesta  # noqa: E402
from modelos.item_cesta import ItemCesta  # noqa: E402
from modelos.produto import Produto  # noqa: E402
from modelos.usuario import Usuario  # noqa: E402
from seguranca import criar_hash_de_senha  # noqa: E402


BANCO_DE_TESTE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessaoDeTeste = sessionmaker(bind=BANCO_DE_TESTE, autoflush=False, autocommit=False)


def obter_sessao_de_teste() -> Generator[Session, None, None]:
    """Entrega uma sessao SQLite para cada requisicao do cliente de teste."""

    sessao = SessaoDeTeste()
    try:
        yield sessao
    finally:
        sessao.close()


@pytest.fixture
def cliente() -> Generator[TestClient, None, None]:
    """Cria um banco limpo e um cliente HTTP para cada teste."""

    # Cada teste começa com as janelas de protecao vazias.
    limitador.resetar()
    Base.metadata.create_all(bind=BANCO_DE_TESTE)
    sessao = SessaoDeTeste()
    sessao.add_all(
        [
            Usuario(
                usuario="aline",
                email="aline@teste.local",
                senha_hash=criar_hash_de_senha("aline123"),
                perfil="assinante",
                ativo=True,
            ),
            Usuario(
                usuario="vanderlei",
                email="vanderlei@teste.local",
                senha_hash=criar_hash_de_senha("vanderlei123"),
                perfil="produtor",
                ativo=True,
            ),
            *[
                Produto(id=produto_id, nome=produto_id.title())
                for produto_id in (
                    "alface",
                    "tomate",
                    "cenoura",
                    "batata",
                    "cebola",
                    "couve",
                    "beterraba",
                    "abobrinha",
                    "chuchu",
                    "pimentao",
                    "pepino",
                    "mandioca",
                )
            ],
        ]
    )
    sessao.flush()
    assinante = sessao.query(Usuario).filter_by(usuario="aline").one()
    produtor = sessao.query(Usuario).filter_by(usuario="vanderlei").one()
    sessao.add_all(
        [
            Cesta(
                assinante=assinante.usuario,
                usuario_id=assinante.id,
                semana=date(2026, 10, 19),
                tamanho="pequena",
                tamanho_nome="Pequena",
                modo="pronta",
                limite=5,
                situacao="Pendente",
                itens=[ItemCesta(produto_id="alface", quantidade=2)],
            ),
            Cesta(
                assinante=produtor.usuario,
                usuario_id=produtor.id,
                semana=date(2026, 10, 19),
                tamanho="media",
                tamanho_nome="Media",
                modo="selecionavel",
                limite=8,
                situacao="Pendente",
                itens=[ItemCesta(produto_id="alface", quantidade=1)],
            ),
        ]
    )
    sessao.commit()
    sessao.close()

    app.dependency_overrides[obter_sessao] = obter_sessao_de_teste
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=BANCO_DE_TESTE)


def fazer_login(cliente: TestClient, usuario: str, senha: str) -> str:
    """Realiza login e retorna o cookie para os testes que usam Bearer."""

    resposta = cliente.post("/autenticacao/login", json={"usuario": usuario, "senha": senha})
    assert resposta.status_code == 200
    return cliente.cookies.get("access_token")
