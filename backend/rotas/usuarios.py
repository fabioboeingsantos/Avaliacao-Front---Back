"""Rotas públicas para cadastro e consulta da conta autenticada."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from banco import obter_sessao
from rotas.autenticacao import exigir_permissao
from esquemas.usuario import DadosCadastroUsuario, UsuarioPublico
from servicos import usuario as servico
from servicos.excecoes import UsuarioJaExiste


router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("", response_model=UsuarioPublico, status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(
    dados: DadosCadastroUsuario,
    sessao: Session = Depends(obter_sessao),
):
    """Cria uma conta pública com perfil inicial de assinante."""

    try:
        return servico.cadastrar(sessao, dados.usuario, dados.email, dados.senha)
    except UsuarioJaExiste as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro)) from erro


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
