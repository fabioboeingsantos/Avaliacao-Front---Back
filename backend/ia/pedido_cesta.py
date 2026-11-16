"""Interpreta um pedido de cesta em uma proposta estruturada, sem gravar dados."""

import json
import os
import re
import unicodedata
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ia.contexto import carregar_catalogo
from ia.consultas import normalizar
from ia.contratos import ItemProposta, PropostaAgente, ResultadoQA
from ia.modelos import criar_llm
from ia.provedores.contrato import AssistenteIndisponivel
from ia.provedores import simulado
from ia.validacao import itens_fora_catalogo, validar_proposta
from servicos.cesta import LIMITES_POR_TAMANHO, regras_publicas_cesta


class EntradaPropostaCesta(BaseModel):
    """Validar a mensagem recebida pela rota dedicada à proposta de cesta."""

    model_config = ConfigDict(extra="forbid")
    mensagem: str = Field(min_length=1, max_length=2000)
    rascunho: PropostaAgente | None = None

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


class ProdutoParaPrevia(BaseModel):
    id: str
    nome: str
    preco_unitario: float


class FaltaNaCesta(BaseModel):
    produto_id: str
    nome: str
    quantidade: int
    alternativas: list[ProdutoParaPrevia]


class ResultadoPropostaCesta(BaseModel):
    """Manter o formato que a tela usa para mostrar e confirmar uma proposta."""

    model_config = ConfigDict(extra="forbid")
    modo: Literal["simulado", "openrouter"]
    agente: Literal["assinante"]
    status: Literal["proposta", "esclarecimento", "fora_do_escopo"]
    proposta: PropostaAgente | None
    qa: ResultadoQA
    mensagem: str
    rascunho: PropostaAgente | None = None
    falta: FaltaNaCesta | None = None
    precos: list[ProdutoParaPrevia] = Field(default_factory=list)


class EntradaSubstituicao(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rascunho: PropostaAgente
    produto_id: str = Field(min_length=1, max_length=40)
    substituto_id: str | None = Field(default=None, min_length=1, max_length=40)


INSTRUCAO = """
Você interpreta um único pedido de cesta para uma assinante do Cesta do Vale.
Use somente a mensagem, o catálogo e as regras recebidas. Não invente produtos ou IDs.
Retorne uma proposta de cesta selecionável ou pronta somente quando houver informação suficiente.
Use os IDs do catálogo e respeite os limites de produtos distintos e de até 10 unidades por produto.
Para uma cesta selecionável, mantenha os produtos cadastrados solicitados e suas quantidades na proposta,
mesmo se faltar estoque. O sistema vai oferecer escolhas. Não substitua nem omita produtos pedidos.
Se algum produto solicitado não existir no catálogo, peça esclarecimento e identifique o produto na mensagem.
Quando a pessoa pedir cesta pronta, use a composição pronta definida nas regras.
Quando faltar uma informação necessária, houver ambiguidade ou pedido fora do tema,
retorne esclarecimento ou fora_do_escopo sem proposta e faça uma pergunta curta em português do Brasil.
Quando houver rascunho_atual, aplique a mensagem como ajuste ao rascunho.
Preserve tamanho, modo, exclusões e quantidades que a pessoa não pediu para alterar.
Em uma troca, preserve a quantidade original salvo pedido explícito. Peça esclarecimento quando necessário.
Só inicie uma cesta do zero se a pessoa pedir explicitamente.
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


def _avaliar_proposta(modo, proposta, catalogo):
    por_id = {produto["id"]: produto for produto in catalogo}
    erros = validar_proposta(proposta, "assinante", catalogo, [], conferir_estoque=False)
    if erros:
        return _formatar_resultado(modo, "esclarecimento", None, erros[0], duvidas=[erros[0]], problemas=erros)

    if proposta.modo == "selecionavel":
        ids_reservados = {item.produto_id for item in proposta.produtos} | set(proposta.produtos_excluidos)
        for item in proposta.produtos:
            produto = por_id[item.produto_id]
            if item.quantidade <= produto["estoque"]:
                continue
            alternativas = [
                ProdutoParaPrevia.model_validate(outro)
                for outro in catalogo
                if outro["id"] not in ids_reservados
                and outro["categoria"] == produto["categoria"]
                and outro["estoque"] >= item.quantidade
            ]
            mensagem = f"Não há {item.quantidade} un. de {produto['nome']} disponíveis para sua cesta."
            resultado = _formatar_resultado(modo, "esclarecimento", None, mensagem, duvidas=[mensagem])
            resultado.rascunho = proposta
            resultado.falta = FaltaNaCesta(
                produto_id=item.produto_id, nome=produto["nome"],
                quantidade=item.quantidade, alternativas=alternativas,
            )
            return resultado
    elif any(item.quantidade > por_id[item.produto_id]["estoque"] for item in proposta.produtos):
        mensagem = "A cesta pronta está indisponível. Escolha outro tamanho ou monte uma cesta selecionável."
        return _formatar_resultado(modo, "esclarecimento", None, mensagem, duvidas=[mensagem])

    resultado = _formatar_resultado(modo, "proposta", proposta, "Confira a proposta antes de continuar.")
    resultado.precos = [ProdutoParaPrevia.model_validate(por_id[item.produto_id]) for item in proposta.produtos]
    return resultado


def substituir_produto(dados: EntradaSubstituicao, sessao):
    """Revalidar o rascunho e a escolha no catálogo atual, sem gravar o pedido."""
    proposta = dados.rascunho
    catalogo = carregar_catalogo(sessao)
    modo = "simulado" if os.getenv("ASSISTENTE_MODO", "simulado").strip().lower() == "simulado" else "openrouter"
    atual = _avaliar_proposta(modo, proposta, catalogo)
    falta = atual.falta
    if falta is None or falta.produto_id != dados.produto_id:
        if atual.status == "proposta":
            atual.mensagem = "O estoque mudou e a composição original está disponível. Confira a proposta antes de confirmar."
        return atual
    if dados.substituto_id is not None and dados.substituto_id not in {p.id for p in falta.alternativas}:
        atual.mensagem = f"A opção escolhida ficou indisponível para {falta.nome}. Confira as opções atuais."
        return atual
    itens = [
        item.model_copy(update={"produto_id": dados.substituto_id}) if item.produto_id == falta.produto_id else item
        for item in proposta.produtos
        if item.produto_id != falta.produto_id or dados.substituto_id is not None
    ]
    if not itens:
        mensagem = "A cesta ficou vazia. Envie um novo pedido com pelo menos um produto."
        return _formatar_resultado(modo, "esclarecimento", None, mensagem, duvidas=[mensagem])
    return _avaliar_proposta(modo, proposta.model_copy(update={"produtos": itens}), catalogo)


def _executar_modo_simulado(mensagem, catalogo):
    """Manter a demonstração local disponível sem chamar provedores externos."""
    resultado = simulado.analisar(mensagem, "assinante", catalogo, [], historico=None)
    status = resultado.get("status")
    proposta_simulada = resultado.get("proposta")
    if proposta_simulada and 1 <= len(proposta_simulada["produtos"]) <= 12 and all(
        1 <= item["quantidade"] <= 10 for item in proposta_simulada["produtos"]
    ) and len(proposta_simulada["produtos_excluidos"]) <= 12:
        # O chat simulado também inclui o nome de exibição em cada produto.
        produtos = [
            {"produto_id": item["produto_id"], "quantidade": item["quantidade"]}
            for item in proposta_simulada["produtos"]
        ]
        proposta = PropostaAgente.model_validate({**proposta_simulada, "produtos": produtos})
        _ajustar_tamanho_selecionavel(proposta, mensagem)
        return _avaliar_proposta("simulado", proposta, catalogo)
    if status == "esclarecimento":
        duvidas = resultado.get("qa", {}).get("duvidas", [])
        mensagem_resposta = resultado.get("mensagem") or "Pode esclarecer seu pedido?"
        return _formatar_resultado(
            "simulado", "esclarecimento", None, mensagem_resposta,
            duvidas=duvidas or [mensagem_resposta],
        )
    mensagem_resposta = resultado.get("mensagem") or "Esta função ajuda somente a montar propostas de cesta."
    return _formatar_resultado("simulado", "fora_do_escopo", None, mensagem_resposta)


NUMEROS = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5,
    "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10,
}


def _numeros_em_algarismos(texto):
    return re.sub(r"\b(?:" + "|".join(NUMEROS) + r")\b(?=\s+(?!cesta\b))",
                  lambda trecho: str(NUMEROS[trecho.group()]), texto)


def _ajuste_direto(mensagem, rascunho, catalogo):
    """Aplicar ajustes explícitos como um conjunto, preservando os demais itens."""
    aliases = {}
    for produto in catalogo:
        nome = normalizar(produto["nome"])
        plural = nome[:-2] + "oes" if nome.endswith("ao") else nome + "s"
        for alias in {nome, plural, normalizar(produto["id"])}:
            aliases.setdefault(alias, set()).add(produto["id"])

    def identificar(nome):
        nome = re.sub(r"^(?:o|a|os|as)\s+", "", nome.strip())
        ids = aliases.get(nome, set())
        return next(iter(ids)) if len(ids) == 1 else None

    texto = _numeros_em_algarismos(normalizar(mensagem))
    tamanho = re.fullmatch(r"(?:mude para|troque para|deixa|deixe|quero)?\s*(?:cesta\s+)?(pequena|media|grande)[.!? ]*", texto)
    if tamanho:
        return rascunho.model_copy(update={"tamanho": tamanho[1]})
    partes = re.split(r"[.;,]+|\s+e\s+", texto.strip(" !?."))
    itens = {item.produto_id: item.quantidade for item in rascunho.produtos}
    excluidos = set(rascunho.produtos_excluidos)
    for parte in filter(None, map(str.strip, partes)):
        troca = re.fullmatch(r"(?:troca|troque|substitua)\s+(.+?)\s+por\s+(.+)", parte)
        remocao = re.fullmatch(r"(?:sem|tira|tire|retira|retire|remova|exclua)\s+(.+)", parte)
        quantidade = re.fullmatch(
            r"(?:(deixa|deixe|so|apenas|coloque|inclua|adicione|acrescente)\s+)?"
            r"(?:so\s+|apenas\s+)?(\d{1,2})\s+(?:unidades? de\s+)?(.+)", parte,
        )
        if troca:
            origem, destino = map(identificar, troca.groups())
            if origem not in itens or not destino or origem == destino:
                raise ValueError("Informe um produto da cesta e o nome de outro produto do catálogo para fazer a troca.")
            itens[destino] = itens.get(destino, 0) + itens.pop(origem)
            excluidos.add(origem)
            excluidos.discard(destino)
        elif remocao:
            produto_id = identificar(remocao[1])
            if produto_id not in itens:
                raise ValueError("Qual produto da cesta você quer retirar?")
            itens.pop(produto_id)
            excluidos.add(produto_id)
        elif quantidade:
            produto_id = identificar(quantidade[3])
            if not produto_id:
                raise ValueError("Confira o nome do produto no catálogo e envie o ajuste novamente.")
            total = int(quantidade[2])
            if quantidade[1] in {"inclua", "adicione", "acrescente"}:
                total += itens.get(produto_id, 0)
            itens[produto_id] = total
            excluidos.discard(produto_id)
        else:
            return None

    if not itens:
        raise ValueError("Mantenha pelo menos um produto na cesta ou cancele a montagem.")
    if len(itens) > 12 or len(excluidos) > 12 or any(not 1 <= q <= 10 for q in itens.values()):
        raise ValueError("Revise as quantidades. Cada produto deve ter de 1 a 10 unidades e a cesta comporta até 12 produtos.")
    return rascunho.model_copy(update={
        "produtos": [ItemProposta(produto_id=id_, quantidade=q) for id_, q in itens.items()],
        "produtos_excluidos": sorted(excluidos),
    })


def propor_cesta(mensagem: str, sessao, rascunho: PropostaAgente | None = None) -> ResultadoPropostaCesta:
    """Gerar uma única proposta e validá-la localmente sem persistir o resultado."""
    catalogo_completo = carregar_catalogo(sessao)
    catalogo = [
        {campo: produto[campo] for campo in ("id", "nome", "estoque", "categoria")}
        for produto in catalogo_completo
    ]
    modo = os.getenv("ASSISTENTE_MODO", "simulado").strip().lower()
    if modo not in {"simulado", "openrouter"}:
        raise AssistenteIndisponivel("Configure ASSISTENTE_MODO como simulado ou openrouter.")
    if rascunho:
        if rascunho.tipo != "pedido_cesta":
            texto = "Selecione um rascunho de cesta para ajustar."
            return _formatar_resultado(modo, "esclarecimento", None, texto, duvidas=[texto])
        if re.search(r"\b(?:nova cesta|outra cesta|comecar de novo)\b", normalizar(mensagem)):
            rascunho = None
        elif rascunho.modo == "selecionavel":
            try:
                proposta = _ajuste_direto(mensagem, rascunho, catalogo_completo)
            except ValueError as erro:
                return _formatar_resultado(modo, "esclarecimento", None, str(erro), duvidas=[str(erro)])
            if proposta is not None:
                return _avaliar_proposta(modo, proposta, catalogo_completo)
    if rascunho and modo == "simulado":
        texto = "Qual item você quer ajustar? Experimente “só um tomate” ou “troque a couve por alface”."
        return _formatar_resultado(modo, "esclarecimento", None, texto, duvidas=[texto])
    if modo == "simulado":
        return _executar_modo_simulado(_numeros_em_algarismos(normalizar(mensagem)), catalogo_completo)

    # Limitar a entrada externa à mensagem, ao catálogo disponível e às regras públicas da cesta.
    contexto = {
        "mensagem": mensagem,
        "catalogo_disponivel": [produto for produto in catalogo if produto["estoque"] > 0],
        "catalogo_esgotado": [produto for produto in catalogo if produto["estoque"] <= 0],
        "regras_cesta": regras_publicas_cesta(),
    }
    if rascunho:
        contexto["rascunho_atual"] = rascunho.model_dump()
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
    # A lista explícita pode conter um item que o modelo deixou de fora da proposta.
    lista_pedida = re.split(r"\bpara\s+(?!favor\b)", mensagem, maxsplit=1, flags=re.IGNORECASE)[0]
    desconhecidos = itens_fora_catalogo(lista_pedida, catalogo_completo)
    if desconhecidos:
        orientacao = "Reescreva o ajuste." if rascunho else "Reenvie a cesta com os produtos desejados."
        texto = f"Confira os nomes dos produtos fora do catálogo: {', '.join(desconhecidos)}. {orientacao}"
        return _formatar_resultado(modo, "esclarecimento", None, texto, duvidas=[texto])
    return _avaliar_proposta(modo, proposta, catalogo_completo)
