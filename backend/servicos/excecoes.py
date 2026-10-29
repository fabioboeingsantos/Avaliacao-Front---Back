"""Excecoes de dominio traduzidas em respostas pela camada HTTP."""


class ErroDeAplicacao(Exception):
    """Base para recusas conhecidas da regra de negocio."""


class UsuarioJaExiste(ErroDeAplicacao):
    """Indica que nome de usuário ou e-mail já está cadastrado."""


class CestaNaoEncontrada(ErroDeAplicacao):
    """Indica que o identificador da cesta nao existe."""


class AcessoNegado(ErroDeAplicacao):
    """Indica que o perfil atual nao pode executar a operacao."""


class TamanhoInvalido(ErroDeAplicacao):
    """Indica que o tamanho informado nao possui limite cadastrado."""


class ProdutoNaoEncontrado(ErroDeAplicacao):
    """Indica que o produto nao esta no catalogo."""


class EstoqueInsuficiente(ErroDeAplicacao):
    """Indica que o estoque disponivel nao atende a quantidade pedida."""


class ProdutoNaoPertenceCesta(ErroDeAplicacao):
    """Indica que o produto nao faz parte da cesta informada."""


class QuantidadeExcedida(ErroDeAplicacao):
    """Indica que a quantidade solicitada ultrapassa o que ainda cabe."""


class SemanaInvalida(ErroDeAplicacao):
    """Indica que a semana nao esta no formato esperado."""
