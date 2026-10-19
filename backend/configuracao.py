"""Configurações da API e da conexão persistente."""

import os

from dotenv import load_dotenv
from sqlalchemy import URL


load_dotenv()


def obter_url_banco() -> URL:
    """Monta a URL do banco a partir das chaves do ambiente."""

    driver = os.getenv("BANCO_DRIVER", "sqlite")
    database = os.getenv("BANCO_NOME", "./cesta_do_vale.db")

    if driver.startswith("sqlite"):
        return URL.create(drivername=driver, database=database)

    porta = os.getenv("BANCO_PORTA")
    return URL.create(
        drivername=driver,
        username=os.getenv("BANCO_USUARIO"),
        password=os.getenv("BANCO_SENHA"),
        host=os.getenv("BANCO_HOST"),
        port=int(porta) if porta else None,
        database=database,
    )


def obter_origens_frontend() -> list[str]:
    """Le a origem permitida, mantendo o Vite local como padrao."""

    origem = os.getenv("FRONTEND_URL", "http://localhost:5173")
    return [origem]


def obter_chave_jwt() -> str:
    """Retorna a chave usada para assinar os tokens de acesso."""

    chave = os.getenv("JWT_SECRET_KEY")
    if not chave or len(chave) < 32:
        raise RuntimeError("Configure JWT_SECRET_KEY com pelo menos 32 caracteres.")
    return chave


def obter_algoritmo_jwt() -> str:
    """Define o algoritmo de assinatura usado pelos tokens."""

    return os.getenv("JWT_ALGORITHM", "HS256")


def obter_duracao_token_minutos() -> int:
    """Define por quantos minutos um token de acesso permanece valido."""

    valor = os.getenv("JWT_EXPIRATION_MINUTES", "30")
    try:
        duracao = int(valor)
    except ValueError as erro:
        raise RuntimeError("JWT_EXPIRATION_MINUTES deve ser um numero inteiro.") from erro

    if duracao <= 0:
        raise RuntimeError("JWT_EXPIRATION_MINUTES deve ser maior que zero.")
    return duracao


def obter_nome_cookie_jwt() -> str:
    """Define o nome do cookie HttpOnly que guarda a sessao."""

    return os.getenv("JWT_COOKIE_NAME", "access_token")


def obter_cookie_seguro() -> bool:
    """Ativa HTTPS obrigatorio para o cookie quando configurado no ambiente."""

    return os.getenv("JWT_COOKIE_SECURE", "false").lower() == "true"
