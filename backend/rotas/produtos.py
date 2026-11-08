"""Rotas do catálogo e do estoque disponível."""

from fastapi import APIRouter, Depends, HTTPException, status
import re
import unicodedata
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from banco import obter_sessao
from esquemas.cesta import AtualizarCategoria, AtualizarEstoque, AtualizarPreco, NovoProduto
from repositorios import cesta as repositorio
from rotas.autenticacao import exigir_permissao
from modelos.usuario import Usuario
from modelos.produto import Produto


router = APIRouter(prefix="/produtos", tags=["Produtos e estoque"])


@router.post("", status_code=status.HTTP_201_CREATED)
def adicionar_produto(
    dados: NovoProduto,
    sessao: Session = Depends(obter_sessao),
    _usuario: Usuario = Depends(exigir_permissao("produtos.criar")),
):
    """Cadastra um item do catálogo exclusivamente pelo perfil produtor."""
    nome_ascii = unicodedata.normalize("NFKD", dados.nome).encode("ascii", "ignore").decode().lower()
    identificador = re.sub(r"[^a-z0-9]+", "-", nome_ascii).strip("-")[:40].rstrip("-")
    if not identificador:
        raise HTTPException(status_code=422, detail="Informe um nome de produto válido.")
    produto = Produto(id=identificador, nome=dados.nome, categoria=dados.categoria,
                      estoque=dados.estoque, preco_centavos=int(dados.preco_unitario * 100))
    sessao.add(produto)
    try:
        sessao.commit()
    except IntegrityError:
        sessao.rollback()
        raise HTTPException(status_code=409, detail="Já existe um produto com esse nome. Atualize o item cadastrado.") from None
    return {"id": produto.id, "nome": produto.nome, "categoria": produto.categoria,
            "estoque": produto.estoque, "preco_unitario": produto.preco_centavos / 100}


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
            "categoria": produto["categoria"],
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


@router.put("/{produto_id}/categoria")
def definir_categoria(
    produto_id: str,
    dados: AtualizarCategoria,
    sessao: Session = Depends(obter_sessao),
    _usuario: Usuario = Depends(exigir_permissao("produtos.atualizar_estoque")),
):
    """Permite ao produtor classificar o produto cadastrado."""
    produto = repositorio.atualizar_categoria(sessao, produto_id, dados.categoria)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
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
