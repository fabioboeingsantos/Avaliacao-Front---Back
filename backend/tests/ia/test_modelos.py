"""Confere a montagem da cadeia de provedores sem rede ou uso de cota."""

from unittest.mock import patch

import pytest

from ia.provedores.contrato import AssistenteIndisponivel
from ia.modelos import criar_llm


class LLMFalso:
    """Substituir o cliente Jangada para inspecionar os provedores configurados."""

    instancias = []

    def __init__(self, provedor, modelo, **opcoes):
        self.provedor = provedor
        self.modelo = modelo
        self.opcoes = opcoes
        self.reservas = []
        self.__class__.instancias.append(self)

    def with_fallback(self, reserva):
        """Registrar o fallback pedido pelo código sem chamar um provedor real."""
        self.reservas.append(reserva)
        return self


@pytest.fixture(autouse=True)
def preparar_ambiente(monkeypatch):
    """Usar valores fictícios e limpar o estado entre os cenários."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia-openrouter")
    monkeypatch.setenv("GEMINI_API_KEY", "chave-ficticia-gemini")
    monkeypatch.setenv("IA_MODELO_PADRAO", "openrouter/free")
    monkeypatch.setenv("IA_GEMINI_FALLBACK_MODEL", "gemini-ficticio")
    monkeypatch.setenv("IA_FALLBACK_JANGADA", "true")
    LLMFalso.instancias = []
    with patch("jangada_ai.LLM", LLMFalso):
        yield


def test_criar_llm_mantem_openrouter_principal_e_gemini_reserva():
    """Confirmar a ordem configurada sem enviar uma requisição externa."""
    llm = criar_llm()

    principal, reserva = LLMFalso.instancias
    assert llm is principal
    assert (principal.provedor, principal.modelo) == ("openrouter", "openrouter/free")
    assert (reserva.provedor, reserva.modelo) == ("gemini", "gemini-ficticio")
    assert principal.reservas == [reserva]
    assert principal.opcoes["extra"]["provider"]["max_price"] == {"prompt": 0, "completion": 0}


def test_criar_llm_pode_desligar_fallback(monkeypatch):
    """Permitir verificar o provedor principal sem ativar a reserva."""
    monkeypatch.setenv("IA_FALLBACK_JANGADA", "false")

    llm = criar_llm()

    assert llm is LLMFalso.instancias[0]
    assert llm.reservas == []


def test_chave_principal_ausente_interrompe_antes_de_criar_clientes(monkeypatch):
    """Evitar inicializar provedores quando falta a configuração principal."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "")

    with pytest.raises(AssistenteIndisponivel):
        criar_llm()

    assert LLMFalso.instancias == []
