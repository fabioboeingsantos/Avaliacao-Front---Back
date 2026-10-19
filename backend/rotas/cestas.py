"""Rotas REST do domínio de cestas."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from banco import obter_sessao
from rotas.autenticacao import obter_conta_atual
from esquemas.cesta import NovaCesta, NovaSeparacao
from servicos import cesta as servico
from servicos.excecoes import AcessoNegado, CestaNaoEncontrada, ErroDeAplicacao
from modelos.usuario import Usuario


router = APIRouter(prefix="/cestas", tags=["Cestas"])


def traduzir_erro(erro: ErroDeAplicacao) -> HTTPException:
    """Converte uma recusa do servico no status HTTP preservado pela rota."""

    codigo = (
        status.HTTP_404_NOT_FOUND
        if isinstance(erro, CestaNaoEncontrada)
        else status.HTTP_403_FORBIDDEN
        if isinstance(erro, AcessoNegado)
        else status.HTTP_422_UNPROCESSABLE_ENTITY
    )
    return HTTPException(status_code=codigo, detail=str(erro))


@router.get("")
def listar_cestas(
    assinante: str | None = Query(default=None),
    tamanho: str | None = Query(default=None),
    sessao: Session = Depends(obter_sessao),
    conta: Usuario = Depends(obter_conta_atual),
):
    """Lista as cestas e aceita filtro por assinante e tamanho."""

    usuario_id = conta.id if conta.perfil == "assinante" else None
    filtro_assinante = conta.usuario if conta.perfil == "assinante" else assinante
    return servico.listar_cestas(
        sessao,
        assinante=filtro_assinante,
        tamanho=tamanho,
        usuario_id=usuario_id,
    )


@router.get("/{id_cesta}")
def mostrar_cesta(
    id_cesta: int,
    sessao: Session = Depends(obter_sessao),
    conta: Usuario = Depends(obter_conta_atual),
):
    """Mostra uma cesta completa, incluindo sua composição e situação."""

    try:
        usuario_id = conta.id if conta.perfil == "assinante" else None
        return servico.serializar_cesta(servico.buscar_cesta(sessao, id_cesta, usuario_id=usuario_id))
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.post("", status_code=status.HTTP_201_CREATED)
def pedir_cesta(
    dados: NovaCesta,
    sessao: Session = Depends(obter_sessao),
    conta: Usuario = Depends(obter_conta_atual),
):
    """Cria uma cesta com situação inicial pedida."""

    try:
        if conta.perfil != "assinante":
            raise AcessoNegado("Somente assinantes podem criar cestas.")
        dados_cesta = dados.model_dump()
        # O dono vem do token; o campo enviado pelo cliente nao define a propriedade.
        dados_cesta["assinante"] = conta.usuario
        return servico.criar_cesta(sessao, dados_cesta, usuario_id=conta.id)
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.get("/{id_cesta}/separacoes")
def listar_separacoes(
    id_cesta: int,
    sessao: Session = Depends(obter_sessao),
    conta: Usuario = Depends(obter_conta_atual),
):
    """Lista os produtos já separados de uma cesta."""

    try:
        usuario_id = conta.id if conta.perfil == "assinante" else None
        return servico.listar_separacoes(sessao, id_cesta, usuario_id=usuario_id)
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.post("/{id_cesta}/separacoes")
def registrar_separacao(
    id_cesta: int,
    dados: NovaSeparacao,
    sessao: Session = Depends(obter_sessao),
    conta: Usuario = Depends(obter_conta_atual),
):
    """Registra um produto separado aplicando as regras de balanço da cesta."""

    try:
        if conta.perfil != "produtor":
            raise AcessoNegado("Somente produtores podem registrar separacoes.")
        return servico.separar_produto(sessao, id_cesta, dados.produto_id, dados.quantidade)
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro
