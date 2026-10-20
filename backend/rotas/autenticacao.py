"""Rotas de acesso ao sistema."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from banco import obter_sessao
from configuracao import obter_cookie_seguro, obter_duracao_token_minutos, obter_nome_cookie_jwt
from esquemas.usuario import DadosLogin, SessaoUsuario
from modelos.usuario import Usuario
from repositorios import usuario as repositorio_de_usuarios
from servicos import usuario as servico
from seguranca import criar_token_de_acesso, ler_token_de_acesso


esquema_bearer = HTTPBearer(auto_error=False)


def obter_usuario_atual(
    requisicao: Request,
    credenciais: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
    sessao: Session = Depends(obter_sessao),
) -> Usuario:
    """Aceita Bearer legado ou o cookie HttpOnly emitido pelo login."""

    token = None
    if credenciais is not None and credenciais.scheme.lower() == "bearer":
        token = credenciais.credentials
    if token is None:
        token = requisicao.cookies.get(obter_nome_cookie_jwt())

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    dados_token = ler_token_de_acesso(token)
    if dados_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso invalido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = repositorio_de_usuarios.buscar_por_usuario(sessao, dados_token["sub"])
    if usuario is None or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A conta autenticada nao esta disponivel.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario


def obter_conta_atual(
    usuario: Usuario = Depends(obter_usuario_atual),
) -> Usuario:
    """Mantem compatibilidade para dependencias antigas de conta autenticada."""

    return usuario


router = APIRouter(prefix="/autenticacao", tags=["Autenticação"])


@router.post("/login", response_model=SessaoUsuario)
def fazer_login(
    dados: DadosLogin,
    resposta: Response,
    sessao: Session = Depends(obter_sessao),
):
    """Valida o login e informa qual área deve ser apresentada."""

    identificador = dados.email or dados.usuario
    if identificador is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Informe o e-mail ou o usuário.",
        )

    usuario = servico.autenticar(sessao, identificador, dados.senha)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
        )

    token = criar_token_de_acesso(usuario["usuario"], usuario["perfil"])
    # O navegador guarda o token sem permitir acesso por JavaScript.
    resposta.set_cookie(
        key=obter_nome_cookie_jwt(),
        value=token,
        max_age=obter_duracao_token_minutos() * 60,
        httponly=True,
        secure=obter_cookie_seguro(),
        samesite="lax",
    )
    return usuario


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def fazer_logout(resposta: Response):
    """Remove a sessao HttpOnly do navegador."""

    resposta.delete_cookie(key=obter_nome_cookie_jwt())
