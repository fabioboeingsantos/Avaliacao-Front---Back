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
    """Lê a origem permitida, mantendo o Vite local como padrão."""

    origem = os.getenv("FRONTEND_URL", "http://localhost:5173")
    return [origem]
