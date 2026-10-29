"""Rotas do catálogo e do estoque disponível."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from banco import obter_sessao
from esquemas.cesta import AtualizarEstoque, AtualizarPreco
from repositorios import cesta as repositorio
from rotas.autenticacao import exigir_permissao
from modelos.usuario import Usuario


router = APIRouter(prefix="/produtos", tags=["Produtos e estoque"])


@router.get("")
def listar_produtos(
    sessao: Session = Depends(obter_sessao),
    _usuario: Usuario = Depends(exigir_permissao("produtos.listar")),
):
    """Lista produtos e suas quantidades disponíveis para o catálogo."""

    return [
        {
            "id": produto["id"],
            "nome": produto["nome"],
            "estoque": produto["estoque"],
            "preco_unitario": produto["preco_centavos"] / 100,
        }
        for produto in repositorio.listar_produtos_disponiveis(sessao)
    ]


@router.put("/{produto_id}/estoque")
def definir_estoque(
    produto_id: str,
    dados: AtualizarEstoque,
    sessao: Session = Depends(obter_sessao),
    _usuario: Usuario = Depends(exigir_permissao("produtos.atualizar_estoque")),
):
    """Permite somente ao produtor definir o estoque disponível."""

    produto = repositorio.atualizar_estoque(sessao, produto_id, dados.quantidade)
    if produto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado.")
    return produto


@router.put("/{produto_id}/preco")
def definir_preco(
    produto_id: str,
    dados: AtualizarPreco,
    sessao: Session = Depends(obter_sessao),
    _usuario: Usuario = Depends(exigir_permissao("produtos.atualizar_preco")),
):
    """Permite somente ao produtor alterar o preço unitário do catálogo."""

    # O banco trabalha em centavos para manter o cálculo monetário exato.
    preco_centavos = int(dados.preco_unitario * 100)
    produto = repositorio.atualizar_preco(sessao, produto_id, preco_centavos)
    if produto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado.")
    return produto
