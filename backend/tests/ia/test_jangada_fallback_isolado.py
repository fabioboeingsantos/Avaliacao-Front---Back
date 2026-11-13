"""Verifica o adaptador Jangada sem banco, rede ou consumo de cota."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from ia.contratos import InterpretacaoAgente
from ia.provedores.contrato import AssistenteIndisponivel
from ia.provedores import jangada_fallback


class LLMFalso:
    """Substitui o SDK para validar a montagem e o contrato do fallback."""

    instancias = []
    resultado = None
    excecao = None

    def __init__(self, provedor, modelo, **opcoes):
        self.provedor = provedor
        self.modelo = modelo
        self.opcoes = opcoes
        self.reservas = []
        self.__class__.instancias.append(self)

    def with_fallback(self, reserva):
        self.reservas.append(reserva)
        return self

    def parse(self, **argumentos):
        self.argumentos = argumentos
        if self.__class__.excecao:
            raise self.__class__.excecao
        return self.__class__.resultado


@pytest.fixture(autouse=True)
def preparar(monkeypatch):
    """Usa credenciais falsas e zera o estado entre cada cenário isolado."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-teste-openrouter")
    monkeypatch.setenv("GEMINI_API_KEY", "chave-teste-gemini")
    monkeypatch.setenv("IA_MODELO_PADRAO", "openrouter/free")
    monkeypatch.setenv("IA_GEMINI_FALLBACK_MODEL", "gemini-3.8-flash")
    monkeypatch.setenv("IA_FALLBACK_JANGADA", "true")
    monkeypatch.setenv("OPENROUTER_MAX_TOKENS", "512")
    LLMFalso.instancias = []
    LLMFalso.excecao = None
    LLMFalso.resultado = SimpleNamespace(
        parsed=InterpretacaoAgente(intencao="Montar cesta", fora_do_escopo=False),
        provider="openrouter",
    )
    with patch("jangada_ai.LLM", LLMFalso):
        yield


def executar():
    """Invoca só uma etapa do agente, sem passar por API, banco ou fluxo."""
    return jangada_fallback.chamar_agente(
        "interprete", "Instrução de teste", {"mensagem_original": "teste"}, InterpretacaoAgente
    )


def test_cria_openrouter_com_gemini_de_reserva_e_valida_resposta():
    resposta = executar()

    assert resposta == InterpretacaoAgente(intencao="Montar cesta", fora_do_escopo=False)
    principal, reserva = LLMFalso.instancias
    assert (principal.provedor, principal.modelo) == ("openrouter", "openrouter/free")
    assert principal.opcoes["max_retries"] == 1
    assert principal.opcoes["extra"]["provider"]["max_price"] == {"prompt": 0, "completion": 0}
    assert principal.reservas == [reserva]
    assert (reserva.provedor, reserva.modelo) == ("gemini", "gemini-3.8-flash")
    assert principal.argumentos["schema"] is InterpretacaoAgente
    assert principal.argumentos["system"] == "Instrução de teste"
    assert principal.argumentos["params"] == {"max_tokens": 512}


def test_sinalizador_desliga_a_reserva(monkeypatch):
    monkeypatch.setenv("IA_FALLBACK_JANGADA", "false")
    executar()
    principal, _reserva = LLMFalso.instancias
    assert principal.reservas == []


def test_falha_interna_vira_erro_seguro_sem_expor_detalhes():
    LLMFalso.excecao = RuntimeError("segredo e conteúdo privado")

    with pytest.raises(AssistenteIndisponivel) as erro:
        executar()

    assert "segredo" not in str(erro.value)
    assert "conteúdo privado" not in str(erro.value)


def test_chave_openrouter_ausente_impede_criar_clientes(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "")

    with pytest.raises(AssistenteIndisponivel, match="OPENROUTER_API_KEY"):
        executar()

    assert LLMFalso.instancias == []


def test_modelo_pago_e_barrado_antes_de_criar_clientes(monkeypatch):
    monkeypatch.setenv("IA_MODELO_PADRAO", "exemplo/modelo-pago")

    with pytest.raises(AssistenteIndisponivel, match=":free"):
        executar()

    assert LLMFalso.instancias == []
