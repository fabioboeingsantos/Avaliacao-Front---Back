"""Rotas de acesso ao sistema."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from banco import obter_sessao
from esquemas.autenticacao import DadosLogin, SessaoUsuario
from servicos import autenticacao as servico


router = APIRouter(prefix="/autenticacao", tags=["Autenticação"])


@router.post("/login", response_model=SessaoUsuario)
def fazer_login(dados: DadosLogin, sessao: Session = Depends(obter_sessao)):
    """Valida o login e informa qual área deve ser apresentada."""

    usuario = servico.autenticar(sessao, dados.usuario, dados.senha)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
        )

    return usuario
