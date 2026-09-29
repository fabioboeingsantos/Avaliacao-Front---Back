"""Rotas REST do domínio de cestas."""

from fastapi import APIRouter, HTTPException, Query, status

from esquemas.cestas import NovaCesta, NovaSeparacao
from servicos import cestas as servico


router = APIRouter(prefix="/cestas", tags=["Cestas"])


@router.get("")
def listar_cestas(
    assinante: str | None = Query(default=None),
    tamanho: str | None = Query(default=None),
):
    """Lista as cestas e aceita filtro por assinante e tamanho."""

    return servico.listar_cestas(assinante=assinante, tamanho=tamanho)


@router.get("/{id_cesta}")
def mostrar_cesta(id_cesta: int):
    """Mostra uma cesta completa, incluindo sua composição e situação."""

    cesta = servico.buscar_cesta(id_cesta)
    if cesta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cesta não encontrada.")
    return cesta


@router.post("", status_code=status.HTTP_201_CREATED)
def pedir_cesta(dados: NovaCesta):
    """Cria uma cesta com situação inicial pedida."""

    try:
        return servico.criar_cesta(dados.model_dump())
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(erro)) from erro


@router.get("/{id_cesta}/separacoes")
def listar_separacoes(id_cesta: int):
    """Lista os produtos já separados de uma cesta."""

    separacoes = servico.listar_separacoes(id_cesta)
    if separacoes is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cesta não encontrada.")
    return separacoes


@router.post("/{id_cesta}/separacoes")
def registrar_separacao(id_cesta: int, dados: NovaSeparacao):
    """Registra um produto separado aplicando a regra de limite."""

    try:
        return servico.separar_produto(id_cesta, dados.produto_id, dados.quantidade)
    except LookupError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(erro)) from erro
