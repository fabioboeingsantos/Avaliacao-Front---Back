"""Esquemas públicos e de entrada para contas de usuário."""

from pydantic import BaseModel, EmailStr, Field, field_validator


def validar_nova_senha(senha: str) -> str:
    comuns = {'12345678', '123456789', '1234567890', 'password', 'password123',
              'senha123', 'senha1234', 'qwerty123', 'abcdefgh', '87654321'}
    if senha.lower() in comuns or len(set(senha)) == 1:
        raise ValueError('Escolha uma senha menos previsível.')
    return senha


class DadosCadastroUsuario(BaseModel):
    """Dados necessários para criar uma conta de assinante."""

    usuario: str = Field(min_length=1, max_length=80)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    _validar_senha = field_validator('senha')(validar_nova_senha)

    @field_validator('usuario', mode='before')
    @classmethod
    def normalizar_usuario(cls, valor):
        if isinstance(valor, str):
            valor = valor.strip().lower()
            if '@' in valor:
                raise ValueError('Use um nome de usuário sem @; informe o e-mail no campo próprio.')
        return valor


class DadosLogin(BaseModel):
    """Login por e-mail ou, durante a transição, pelo usuário existente."""

    email: EmailStr | None = None
    usuario: str | None = Field(default=None, min_length=1, max_length=254)
    senha: str = Field(min_length=1, max_length=128)


class UsuarioPublico(BaseModel):
    """Representação de conta que nunca inclui a senha."""

    id: int
    usuario: str
    email: str
    perfil: str
    grupo: str
    ativo: bool
    email_verificado: bool


class SolicitarEmail(BaseModel):
    email: EmailStr


class ConfirmarToken(BaseModel):
    token: str = Field(min_length=20, max_length=200)


class RedefinirSenha(ConfirmarToken):
    senha: str = Field(min_length=8, max_length=128)
    _validar_senha = field_validator('senha')(validar_nova_senha)


class SessaoUsuario(BaseModel):
    """Dados públicos devolvidos depois do login."""

    usuario: str
    email: str
    perfil: str
    grupo: str
    access_token: str
    token_type: str = "bearer"
