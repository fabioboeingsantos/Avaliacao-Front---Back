"""Esquemas públicos e de entrada para contas de usuário."""

from pydantic import BaseModel, EmailStr, Field


class DadosCadastroUsuario(BaseModel):
    """Dados necessários para criar uma conta de assinante."""

    usuario: str = Field(min_length=1, max_length=80)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)


class DadosLogin(BaseModel):
    """Login por e-mail ou, durante a transição, pelo usuário existente."""

    email: EmailStr | None = None
    usuario: str | None = Field(default=None, min_length=1, max_length=80)
    senha: str = Field(min_length=1, max_length=128)


class UsuarioPublico(BaseModel):
    """Representação de conta que nunca inclui a senha."""

    id: int
    usuario: str
    email: str
    perfil: str
    grupo: str
    ativo: bool


class SessaoUsuario(BaseModel):
    """Dados públicos devolvidos depois do login."""

    usuario: str
    email: str
    perfil: str
    grupo: str
    access_token: str
    token_type: str = "bearer"
