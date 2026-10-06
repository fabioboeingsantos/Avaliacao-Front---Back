"""Consultas de usuários persistidos no banco de dados."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from modelos.usuarios import Usuario


def buscar_usuario(sessao: Session, usuario: str) -> Usuario | None:
    """Localiza uma conta pelo nome normalizado dentro da sessão atual."""

    usuario_normalizado = usuario.strip().lower()
    consulta = select(Usuario).where(Usuario.usuario == usuario_normalizado)
    return sessao.scalars(consulta).first()
