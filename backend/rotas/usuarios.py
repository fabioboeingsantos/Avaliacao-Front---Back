"""Rotas públicas para cadastro e consulta da conta autenticada."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from banco import obter_sessao
from rotas.autenticacao import exigir_permissao
from esquemas.usuario import DadosCadastroUsuario, UsuarioPublico
from limites_autenticacao import (
    limitador,
    obter_duracao_janela,
    obter_endereco_cliente,
    obter_limite_cadastro,
)
from servicos import usuario as servico
from servicos.excecoes import UsuarioJaExiste


router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("", response_model=UsuarioPublico, status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(
    dados: DadosCadastroUsuario,
    requisicao: Request,
    sessao: Session = Depends(obter_sessao),
):
    """Cria uma conta pública com perfil inicial de assinante."""

    # Limita a quantidade de cadastros iniciados pelo mesmo endereco.
    liberado, segundos = limitador.permitir(
        "cadastro-ip",
        obter_endereco_cliente(requisicao),
        obter_limite_cadastro(),
        obter_duracao_janela(),
    )
    if not liberado:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitos cadastros iniciados. Aguarde antes de tentar novamente.",
            headers={"Retry-After": str(segundos)},
        )

    try:
        return servico.cadastrar(sessao, dados.usuario, dados.email, dados.senha)
    except UsuarioJaExiste as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro)) from erro
    except IntegrityError as erro:
        # A restricao UNIQUE do banco tambem protege duas requisicoes simultaneas.
        sessao.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este usuario ou e-mail ja esta cadastrado.",
        ) from erro


@router.get("/me", response_model=UsuarioPublico)
def mostrar_usuario_atual(
    usuario=Depends(exigir_permissao("usuarios.consultar_propria_conta")),
):
    """Retorna os dados públicos da conta autenticada."""

    return servico.serializar_usuario(usuario)


@router.get("/eu", response_model=UsuarioPublico)
def mostrar_usuario_do_token(usuario=Depends(exigir_permissao("usuarios.consultar_propria_conta"))):
    """Retorna os dados presentes no token do usuario autenticado."""

    return servico.serializar_usuario(usuario)
