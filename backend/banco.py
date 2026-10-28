"""Infraestrutura SQLAlchemy compartilhada pela API."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from configuracao import obter_url_banco


URL_DO_BANCO = obter_url_banco()
argumentos_conexao = {"check_same_thread": False} if URL_DO_BANCO.get_backend_name() == "sqlite" else {}

engine = create_engine(
    URL_DO_BANCO,
    poolclass=NullPool,
    pool_pre_ping=True,
    connect_args=argumentos_conexao,
)
Sessao = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Classe-base das tabelas do sistema."""


def obter_sessao() -> Generator[Session, None, None]:
    """Abre uma sessão por requisição e garante seu fechamento."""

    sessao = Sessao()
    try:
        yield sessao
    finally:
        sessao.close()
