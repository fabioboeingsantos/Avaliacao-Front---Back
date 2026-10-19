"""Persistência das contas de usuário."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from modelos.usuario import Usuario


def buscar_por_email(sessao: Session, email: str) -> Usuario | None:
    """Busca uma conta pelo e-mail normalizado."""

    email_normalizado = email.strip().lower()
    consulta = select(Usuario).where(Usuario.email == email_normalizado)
    return sessao.scalars(consulta).first()


def buscar_por_usuario(sessao: Session, usuario: str) -> Usuario | None:
    """Busca uma conta pelo nome de usuário normalizado."""

    usuario_normalizado = usuario.strip().lower()
    consulta = select(Usuario).where(Usuario.usuario == usuario_normalizado)
    return sessao.scalars(consulta).first()


def salvar(sessao: Session, conta: Usuario) -> Usuario:
    """Persiste uma conta e devolve o registro atualizado."""

    sessao.add(conta)
    sessao.commit()
    sessao.refresh(conta)
    return conta
