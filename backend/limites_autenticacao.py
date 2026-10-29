"""Limites simples contra abuso de login e cadastro.

O armazenamento em memoria atende ao prototipo. Em producao com varias
instancias, este componente deve ser substituido por Redis/Upstash ou outro
armazenamento compartilhado.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class RegistroLimite:
    """Conta as tentativas de uma chave durante uma janela de tempo."""

    quantidade: int
    expira_em: float
    bloqueado_ate: float = 0.0


class LimitadorAutenticacao:
    """Aplica janelas e bloqueios temporarios por endereco ou identificador."""

    def __init__(self) -> None:
        self._registros: dict[tuple[str, str], RegistroLimite] = {}
        self._bloqueio = threading.Lock()

    def permitir(self, grupo: str, chave: str, limite: int, janela: int) -> tuple[bool, int]:
        """Permite uma tentativa ou devolve os segundos restantes do bloqueio."""

        agora = time.monotonic()
        identificador = (grupo, chave)
        with self._bloqueio:
            registro = self._registros.get(identificador)
            if registro is None or registro.expira_em <= agora:
                registro = RegistroLimite(quantidade=0, expira_em=agora + janela)
                self._registros[identificador] = registro

            if registro.bloqueado_ate > agora:
                return False, max(1, int(registro.bloqueado_ate - agora))

            if registro.quantidade >= limite:
                registro.bloqueado_ate = agora + obter_duracao_bloqueio()
                logger.warning("Limite de autenticacao atingido: grupo=%s chave=%s", grupo, chave)
                return False, obter_duracao_bloqueio()

            registro.quantidade += 1
            return True, 0

    def limpar(self, grupo: str, chave: str) -> None:
        """Remove falhas acumuladas depois de um login valido."""

        with self._bloqueio:
            self._registros.pop((grupo, chave), None)

    def resetar(self) -> None:
        """Limpa os registros para isolamento dos testes."""

        with self._bloqueio:
            self._registros.clear()


limitador = LimitadorAutenticacao()


def obter_inteiro(nome: str, padrao: int) -> int:
    """Le um limite inteiro do ambiente, usando o padrao em valor invalido."""

    try:
        valor = int(os.getenv(nome, str(padrao)))
    except ValueError:
        return padrao
    return max(1, valor)


def obter_duracao_bloqueio() -> int:
    """Define por quantos segundos uma chave fica bloqueada."""

    return obter_inteiro("AUTH_BLOCK_SECONDS", 900)


def obter_limite_login() -> int:
    """Define quantas tentativas de login cabem na janela."""

    return obter_inteiro("AUTH_LOGIN_LIMIT", 5)


def obter_limite_cadastro() -> int:
    """Define quantos cadastros um endereco pode iniciar na janela."""

    return obter_inteiro("AUTH_SIGNUP_LIMIT", 3)


def obter_duracao_janela() -> int:
    """Define a duracao da janela de controle em segundos."""

    return obter_inteiro("AUTH_RATE_WINDOW_SECONDS", 900)


def obter_endereco_cliente(requisicao) -> str:
    """Obtem o endereco observado pelo servidor sem confiar em cabecalhos livres."""

    return requisicao.client.host if requisicao.client else "desconhecido"
