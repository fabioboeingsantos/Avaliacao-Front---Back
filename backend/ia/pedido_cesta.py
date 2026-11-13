"""Interpreta um pedido de cesta em uma proposta estruturada, sem gravar dados."""

import json
import os
import re
import unicodedata
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ia.contexto import carregar_catalogo
from ia.contratos import PropostaAgente, ResultadoQA
from ia.modelos import criar_llm
from ia.provedores.contrato import AssistenteIndisponivel
from ia.provedores import simulado
from ia.validacao import validar_proposta
from servicos.cesta import LIMITES_POR_TAMANHO, regras_publicas_cesta


class EntradaPropostaCesta(BaseModel):
    """Validar a mensagem recebida pela rota dedicada à proposta de cesta."""

    model_config = ConfigDict(extra="forbid")
    mensagem: str = Field(min_length=1, max_length=2000)

    @field_validator("mensagem")
    @classmethod
    def limpar_mensagem(cls, valor: str) -> str:
        """Recusar mensagens compostas somente por espaços."""
        valor = valor.strip()
        if not valor:
            raise ValueError("Digite seu pedido.")
        return valor


class RespostaModeloCesta(BaseModel):
    """Definir a saída estruturada única solicitada ao modelo."""

    model_config = ConfigDict(extra="forbid")
    status: Literal["proposta", "esclarecimento", "fora_do_escopo"]
    proposta: PropostaAgente | None
    duvidas: list[str] = Field(default_factory=list, max_length=1)
    mensagem: str = Field(min_length=1, max_length=600)


class ResultadoPropostaCesta(BaseModel):
    """Manter o formato que a tela usa para mostrar e confirmar uma proposta."""

    model_config = ConfigDict(extra="forbid")
    modo: Literal["simulado", "openrouter"]
    agente: Literal["assinante"]
    status: Literal["proposta", "esclarecimento", "fora_do_escopo"]
    proposta: PropostaAgente | None
    qa: ResultadoQA
    mensagem: str


INSTRUCAO = """
Você interpreta um único pedido de cesta para uma assinante do Cesta do Vale.
Use somente a mensagem, o catálogo e as regras recebidas. Não invente produtos ou IDs.
Retorne uma proposta de cesta selecionável ou pronta somente quando houver informação suficiente.
Use os IDs do catálogo, respeite estoque, limites de produtos distintos e até 10 unidades por produto.
Quando a pessoa pedir cesta pronta, use a composição pronta definida nas regras.
Quando faltar uma informação necessária, houver ambiguidade, produto indisponível ou pedido fora do tema,
retorne esclarecimento ou fora_do_escopo sem proposta e faça uma pergunta curta em português do Brasil.
Como cada envio é independente, pedir para a pessoa reenviar o pedido completo com a informação que faltou.
Não confirme, grave, altere pedidos, nem execute operações. A pessoa revisará a proposta antes de confirmar.
Retorne somente os campos do formato estruturado.
""".strip()


def _formatar_resultado(modo, status, proposta, mensagem, duvidas=None, problemas=None):
    """Criar a resposta pública sem incluir contexto interno ou dados de conta."""
    aprovada = status == "proposta" and proposta is not None
    if aprovada:
        qa = ResultadoQA(status="aprovado")
    elif status == "esclarecimento":
        qa = ResultadoQA(status="esclarecimento", duvidas=duvidas or [])
    else:
        qa = ResultadoQA(status="bloqueado", problemas=problemas or [])
    return ResultadoPropostaCesta(
        modo=modo,
        agente="assinante",
        status=status,
        proposta=proposta if aprovada else None,
        qa=qa,
        mensagem=mensagem,
    )


def _tamanho_explicito(mensagem):
    """Reconhecer o tamanho escrito pela pessoa para evitar trocar sua escolha silenciosamente."""
    texto = unicodedata.normalize("NFD", mensagem.lower())
    texto = "".join(letra for letra in texto if unicodedata.category(letra) != "Mn")
    padroes = {
        "pequena": r"pequen[ao]s?",
        "media": r"medi[ao]s?",
        "grande": r"grandes?",
    }
    for tamanho, padrao in padroes.items():
        mencionado = re.search(rf"\b{padrao}\b", texto)
        negado = re.search(rf"\b(?:nao|nunca)\s+(?:quero\s+)?{padrao}\b", texto)
        if mencionado and not negado:
            return tamanho
    return None


def _ajustar_tamanho_selecionavel(proposta, mensagem):
    """Preservar tamanho explícito ou escolher o menor que comporta os produtos."""
    tamanho_escrito = _tamanho_explicito(mensagem)
    if proposta.modo != "selecionavel" or not proposta.produtos:
        return
    if tamanho_escrito:
        proposta.tamanho = tamanho_escrito
        return
    if proposta.tamanho:
        return
    quantidade_produtos = len(proposta.produtos)
    proposta.tamanho = next(
        (tamanho for tamanho, limite in LIMITES_POR_TAMANHO.items() if quantidade_produtos <= limite),
        "grande",
    )


def _executar_modo_simulado(mensagem, catalogo):
    """Manter a demonstração local disponível sem chamar provedores externos."""
    resultado = simulado.analisar(mensagem, "assinante", catalogo, [], historico=None)
    status = resultado.get("status")
    if status == "proposta" and resultado.get("proposta"):
        proposta = PropostaAgente.model_validate(resultado["proposta"])
        _ajustar_tamanho_selecionavel(proposta, mensagem)
        erros = validar_proposta(proposta, "assinante", catalogo, [])
        if erros:
            return _formatar_resultado(
                "simulado", "esclarecimento", None, erros[0], duvidas=[erros[0]], problemas=erros,
            )
        return _formatar_resultado(
            "simulado", "proposta", proposta, "Confira a proposta antes de continuar.",
        )
    if status == "esclarecimento":
        duvidas = resultado.get("qa", {}).get("duvidas", [])
        mensagem_resposta = resultado.get("mensagem") or "Pode esclarecer seu pedido?"
        return _formatar_resultado(
            "simulado", "esclarecimento", None, mensagem_resposta,
            duvidas=duvidas or [mensagem_resposta],
        )
    mensagem_resposta = resultado.get("mensagem") or "Esta função ajuda somente a montar propostas de cesta."
    return _formatar_resultado("simulado", "fora_do_escopo", None, mensagem_resposta)


def propor_cesta(mensagem: str, sessao) -> ResultadoPropostaCesta:
    """Gerar uma única proposta e validá-la localmente sem persistir o resultado."""
    catalogo_completo = carregar_catalogo(sessao)
    catalogo = [
        {campo: produto[campo] for campo in ("id", "nome", "estoque", "categoria")}
        for produto in catalogo_completo
    ]
    modo = os.getenv("ASSISTENTE_MODO", "simulado").strip().lower()
    if modo == "simulado":
        return _executar_modo_simulado(mensagem, catalogo_completo)
    if modo != "openrouter":
        raise AssistenteIndisponivel("Configure ASSISTENTE_MODO como simulado ou openrouter.")

    # Limitar a entrada externa à mensagem, ao catálogo disponível e às regras públicas da cesta.
    contexto = {
        "mensagem": mensagem,
        "catalogo_disponivel": [produto for produto in catalogo if produto["estoque"] > 0],
        "regras_cesta": regras_publicas_cesta(),
    }
    try:
        # Usar uma única chamada estruturada da cadeia Jangada, sem agentes ou tools.
        resposta = criar_llm("pedido_cesta").parse(
            prompt=json.dumps(contexto, ensure_ascii=False),
            schema=RespostaModeloCesta,
            system=INSTRUCAO,
            params={"max_tokens": 2048},
        )
        if resposta.parsed is None:
            raise ValueError("Resposta estruturada vazia.")
        interpretacao = RespostaModeloCesta.model_validate(resposta.parsed)
    except AssistenteIndisponivel:
        raise
    except Exception:
        # Ocultar erros internos e manter uma mensagem útil para a continuação manual.
        raise AssistenteIndisponivel(
            "Não foi possível gerar a proposta agora. Tente novamente ou monte a cesta manualmente."
        ) from None

    if interpretacao.status != "proposta" or interpretacao.proposta is None:
        status = "fora_do_escopo" if interpretacao.status == "fora_do_escopo" else "esclarecimento"
        return _formatar_resultado(
            modo, status, None, interpretacao.mensagem,
            duvidas=interpretacao.duvidas or ([interpretacao.mensagem] if status == "esclarecimento" else []),
        )

    proposta = interpretacao.proposta
    if proposta.tipo != "pedido_cesta":
        return _formatar_resultado(
            modo, "fora_do_escopo", None,
            "Posso ajudar a montar uma cesta. Revise ou reescreva seu pedido.",
        )

    _ajustar_tamanho_selecionavel(proposta, mensagem)
    erros = validar_proposta(proposta, "assinante", catalogo_completo, [])
    if erros:
        return _formatar_resultado(
            modo, "esclarecimento", None, erros[0], duvidas=[erros[0]], problemas=erros,
        )

    return _formatar_resultado(
        modo, "proposta", proposta, "Confira a proposta antes de continuar.",
    )
