"""Rotas REST do domínio de cestas."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from banco import obter_sessao
from rotas.autenticacao import exigir_permissao
from esquemas.cesta import DesfazerSeparacoes, NovaCesta, NovasSeparacoes, NovaSeparacao
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
        else status.HTTP_422_UNPROCESSABLE_CONTENT
    )
    return HTTPException(status_code=codigo, detail=str(erro))


@router.get("")
def listar_cestas(
    assinante: str | None = Query(default=None),
    tamanho: str | None = Query(default=None),
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(exigir_permissao("cestas.listar")),
):
    """Lista as cestas e aceita filtro por assinante e tamanho."""

    usuario_id = usuario.id if usuario.perfil == "assinante" else None
    filtro_assinante = usuario.usuario if usuario.perfil == "assinante" else assinante
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
    usuario: Usuario = Depends(exigir_permissao("cestas.consultar")),
):
    """Mostra uma cesta completa, incluindo sua composição e situação."""

    try:
        usuario_id = usuario.id if usuario.perfil == "assinante" else None
        return servico.serializar_cesta(servico.buscar_cesta(sessao, id_cesta, usuario_id=usuario_id))
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.post("", status_code=status.HTTP_201_CREATED)
def pedir_cesta(
    dados: NovaCesta,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(exigir_permissao("cestas.criar")),
):
    """Cria uma cesta com situação inicial pendente."""

    try:
        if usuario.perfil != "assinante":
            raise AcessoNegado("Somente assinantes podem criar cestas.")
        return servico.criar_cesta(
            sessao,
            dados.model_dump(),
            usuario=usuario,
        )
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.post("/{id_cesta}/cancelar")
def cancelar_cesta(
    id_cesta: int,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(exigir_permissao("cestas.cancelar")),
):
    """Permite à assinante cancelar uma cesta que ainda está pendente."""

    try:
        return servico.cancelar_cesta(sessao, id_cesta, usuario.id)
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.get("/{id_cesta}/separacoes")
def listar_separacoes(
    id_cesta: int,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(exigir_permissao("cestas.listar_separacoes")),
):
    """Lista os produtos já separados de uma cesta."""

    try:
        usuario_id = usuario.id if usuario.perfil == "assinante" else None
        return servico.listar_separacoes(sessao, id_cesta, usuario_id=usuario_id)
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.post("/{id_cesta}/separacoes")
def registrar_separacao(
    id_cesta: int,
    dados: NovaSeparacao,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(exigir_permissao("cestas.registrar_separacao")),
):
    """Registra um produto separado aplicando as regras de balanço da cesta."""

    try:
        return servico.separar_produto(sessao, id_cesta, dados.produto_id, dados.quantidade)
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.post("/{id_cesta}/separacoes/lote")
def registrar_separacoes_em_lote(
    id_cesta: int,
    dados: NovasSeparacoes,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(exigir_permissao("cestas.registrar_separacao")),
):
    """Registra vários produtos em uma única operação atômica."""

    try:
        return servico.separar_produtos(
            sessao,
            id_cesta,
            [produto.model_dump() for produto in dados.produtos],
        )
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.post("/{id_cesta}/separacoes/desfazer")
def desfazer_separacoes(
    id_cesta: int,
    dados: DesfazerSeparacoes,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(exigir_permissao("cestas.desfazer_separacao")),
):
    """Desfaz um lote de quantidades registradas pelo produtor."""

    try:
        return servico.desfazer_separacoes(
            sessao,
            id_cesta,
            [produto.model_dump() for produto in dados.produtos],
        )
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.post("/{id_cesta}/separacoes/concluir")
def concluir_separacao(
    id_cesta: int,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(exigir_permissao("cestas.concluir_separacao")),
):
    """Marca a separação como concluída após conferir todos os itens pedidos."""

    try:
        return servico.concluir_separacao(sessao, id_cesta)
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro


@router.post("/{id_cesta}/entrega/confirmar")
def confirmar_entrega(
    id_cesta: int,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(exigir_permissao("cestas.confirmar_entrega")),
):
    """Registra que a assinante recebeu a cesta."""

    try:
        return servico.confirmar_entrega(sessao, id_cesta, usuario.id)
    except ErroDeAplicacao as erro:
        raise traduzir_erro(erro) from erro
