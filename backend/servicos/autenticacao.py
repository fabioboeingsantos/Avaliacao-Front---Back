"""Regras de negócio do acesso ao sistema."""

from secrets import compare_digest

from sqlalchemy.orm import Session

from repositorios import usuarios as repositorio


def autenticar(sessao: Session, usuario: str, senha: str) -> dict | None:
    """Valida credenciais e devolve somente os dados públicos do perfil."""

    conta = repositorio.buscar_usuario(sessao, usuario)
    if conta is None or not compare_digest(conta.senha, senha):
        return None

    return {"usuario": conta.usuario, "perfil": conta.perfil}
