"""Compatibilidade para o repositório de usuários antigo."""

from repositorios.usuario import buscar_por_usuario, salvar


def buscar_usuario(sessao, usuario):
    """Mantém o nome antigo apontando para a busca por usuário."""

    return buscar_por_usuario(sessao, usuario)


__all__ = ["buscar_por_usuario", "buscar_usuario", "salvar"]
