"""Funções centrais de segurança do backend."""

from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from configuracao import (
    obter_algoritmo_jwt,
    obter_chave_jwt,
    obter_duracao_token_minutos,
)


gerador_de_hash = PasswordHash.recommended()


def criar_hash_de_senha(senha: str) -> str:
    """Transforma uma senha em um hash Argon2 irreversível."""

    return gerador_de_hash.hash(senha)


def senha_confere(senha: str, senha_hash: str) -> bool:
    """Confere a senha digitada contra o hash armazenado."""

    try:
        return gerador_de_hash.verify(senha, senha_hash)
    except Exception:
        return False


def senha_ja_esta_protegida(senha_hash: str) -> bool:
    """Evita aplicar hash novamente em um valor já protegido."""

    return senha_hash.startswith("$argon2")


def criar_token_de_acesso(usuario: str, perfil: str) -> str:
    """Cria um JWT assinado com identidade, perfil e expiração."""

    agora = datetime.now(timezone.utc)
    expiracao = agora + timedelta(minutes=obter_duracao_token_minutos())
    dados = {"sub": usuario, "perfil": perfil, "iat": agora, "exp": expiracao}
    return jwt.encode(dados, obter_chave_jwt(), algorithm=obter_algoritmo_jwt())


def ler_token_de_acesso(token: str) -> dict | None:
    """Valida a assinatura e a expiração de um JWT."""

    try:
        dados = jwt.decode(token, obter_chave_jwt(), algorithms=[obter_algoritmo_jwt()])
    except jwt.InvalidTokenError:
        return None

    if not isinstance(dados.get("sub"), str) or not dados.get("sub"):
        return None
    if not isinstance(dados.get("perfil"), str) or not dados.get("perfil"):
        return None
    return dados
