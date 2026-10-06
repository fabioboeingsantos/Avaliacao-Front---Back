"""Rotas REST do domínio de cestas."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from banco import obter_sessao
from esquemas.cesta import NovaCesta, NovaSeparacao
from servicos import cesta as servico
from servicos.excecoes import CestaNaoEncontrada, ErroDeAplicacao


router = APIRouter(prefix="/cestas", tags=["Cestas"])


def traduzir_erro(erro: ErroDeAplicacao) -> HTTPException:
    """Converte uma recusa do servico no status HTTP preservado pela rota."""

    codigo = (
        status.HTTP_404_NOT_FOUND
        if isinstance(erro, CestaNaoEncontrada)
        else status.HTTP_422_UNPROCESSABLE_ENTITY
    )
    return HTTPException(status_code=codigo, detail=str(erro))


@router.get("")
def listar_cestas(
    assinante: str | None = Query(default=None),
    tamanho: str | None = Query(default=None),
    sessao: Session = Depends(obter_sessao),
):
    """Lista as cestas e aceita filtro por assinante e tamanho."""

    return servico.listar_cestas(sessao, assinante=assinante, tamanho=tamanho)


@router.get("/{id_cesta}")
def mostrar_cesta(id_cesta: int, sessao: Session = Depends(obter_sessao)):
    """Mostra uma cesta completa, incluindo sua composição e situação."""

    try:
        return servico.serializar_cesta(servico.buscar_cesta(sessao, id_cesta))
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.post("", status_code=status.HTTP_201_CREATED)
def pedir_cesta(dados: NovaCesta, sessao: Session = Depends(obter_sessao)):
    """Cria uma cesta com situação inicial pedida."""

    try:
        return servico.criar_cesta(sessao, dados.model_dump())
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.get("/{id_cesta}/separacoes")
def listar_separacoes(id_cesta: int, sessao: Session = Depends(obter_sessao)):
    """Lista os produtos já separados de uma cesta."""

    try:
        return servico.listar_separacoes(sessao, id_cesta)
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.post("/{id_cesta}/separacoes")
def registrar_separacao(
    id_cesta: int,
    dados: NovaSeparacao,
    sessao: Session = Depends(obter_sessao),
):
    """Registra um produto separado aplicando as regras de balanço da cesta."""

    try:
        return servico.separar_produto(sessao, id_cesta, dados.produto_id, dados.quantidade)
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro
