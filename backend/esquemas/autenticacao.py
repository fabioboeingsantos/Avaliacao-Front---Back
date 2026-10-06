"""Modelos de entrada e saída do acesso ao sistema."""

from pydantic import BaseModel, Field


class DadosLogin(BaseModel):
    """Credenciais enviadas pelo formulário de acesso."""

    usuario: str = Field(min_length=1)
    senha: str = Field(min_length=1)


class SessaoUsuario(BaseModel):
    """Perfil devolvido depois que as credenciais são validadas."""

    usuario: str
    perfil: str
