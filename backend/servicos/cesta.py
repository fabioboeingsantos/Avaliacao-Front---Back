"""Regras de negocio do fluxo de cestas."""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modelos.usuario import Usuario
from modelos.notificacao import Notificacao
from repositorios import cesta as repositorio
from servicos.excecoes import (
    CestaNaoEncontrada,
    AvaliacaoInvalida,
    EstoqueInsuficiente,
    ProdutoNaoEncontrado,
    ProdutoNaoPertenceCesta,
    QuantidadeExcedida,
    SemanaInvalida,
    TamanhoInvalido,
)


LIMITES_POR_TAMANHO = {
    "pequena": 5,
    "media": 8,
    "grande": 12,
}
LIMITE_UNIDADES_POR_PRODUTO = 10
COMPOSICAO_CESTA_PRONTA = (
    "alface", "tomate", "cenoura", "batata", "cebola", "couve", "beterraba",
    "abobrinha", "chuchu", "pimentao", "pepino", "mandioca",
)


def regras_publicas_cesta() -> dict:
    """Regras estáveis compartilhadas com os agentes e com o cliente da IA."""
    return {
        "limites": LIMITES_POR_TAMANHO.copy(),
        "maximo_unidades": LIMITE_UNIDADES_POR_PRODUTO,
        "composicao_pronta": {
            tamanho: list(COMPOSICAO_CESTA_PRONTA[:limite])
            for tamanho, limite in LIMITES_POR_TAMANHO.items()
        },
    }


def normalizar_tamanho(tamanho: str) -> str:
    """Converte nomes de tamanho para uma chave estavel, sem acentos."""

    tamanho_normalizado = tamanho.strip().lower()
    if tamanho_normalizado in {"media", "medio", "média"}:
        return "media"
    return tamanho_normalizado


def obter_limite(tamanho: str) -> int | None:
    """Retorna o limite do tamanho ou None quando ele nao existe."""

    return LIMITES_POR_TAMANHO.get(normalizar_tamanho(tamanho))


def nome_tamanho(tamanho: str) -> str:
    """Mantem no retorno o nome amigavel usado pela interface."""

    nomes = {"pequena": "Pequena", "media": "Média", "grande": "Grande"}
    return nomes[normalizar_tamanho(tamanho)]


def serializar_cesta(cesta: dict) -> dict:
    """Devolve os dados da cesta no formato usado pela rota e pelo frontend."""

    if cesta.get("situacao") == "Em separação" and cesta.get("separacao_concluida_em"):
        return {**cesta, "situacao": "Preparado para envio"}
    return cesta


def preparar_produtos(sessao: Session, produtos: list[dict]) -> list[tuple[dict, int]]:
    """Confere o catalogo e associa cada item aos dados do produto."""

    catalogo = {produto["id"]: produto for produto in repositorio.listar_produtos_disponiveis(sessao)}
    produtos_preparados = []

    for produto in produtos:
        produto_catalogado = catalogo.get(produto["id"])
        if produto_catalogado is None:
            raise ProdutoNaoEncontrado(f"Produto não encontrado: {produto['id']}")

        produtos_preparados.append((produto_catalogado, produto["quantidade"]))

    return produtos_preparados


def listar_cestas(
    sessao: Session,
    assinante: str | None = None,
    tamanho: str | None = None,
    usuario_id: int | None = None,
) -> list[dict]:
    """Lista cestas aplicando os filtros opcionais da tela do produtor."""

    _marcar_entregues_expiradas(sessao)
    resultado = repositorio.listar_cestas(sessao, usuario_id=usuario_id)

    if assinante:
        resultado = [cesta for cesta in resultado if cesta["assinante"] == assinante]

    if tamanho:
        tamanho_normalizado = normalizar_tamanho(tamanho)
        resultado = [
            cesta for cesta in resultado if normalizar_tamanho(cesta["tamanho"]) == tamanho_normalizado
        ]

    return [serializar_cesta(cesta) for cesta in resultado]


def buscar_cesta(sessao: Session, id_cesta: int, usuario_id: int | None = None) -> dict:
    """Localiza uma cesta pelo identificador informado na URL."""

    _marcar_entregues_expiradas(sessao)
    cesta = repositorio.buscar_cesta_por_id(sessao, id_cesta, usuario_id=usuario_id)
    if cesta is None:
        raise CestaNaoEncontrada("Cesta não encontrada.")
    return serializar_cesta(cesta)


def _marcar_entregues_expiradas(sessao: Session) -> None:
    repositorio.marcar_entregues_expiradas(sessao, datetime.now(timezone.utc))


def criar_cesta(sessao: Session, dados: dict, usuario: Usuario) -> dict:
    """Valida e registra uma nova cesta com situação inicial pendente."""

    limite = obter_limite(dados["tamanho"])
    if limite is None:
        raise TamanhoInvalido("Tamanho inválido. Use pequena, media ou grande.")

    produtos = preparar_produtos(sessao, dados["produtos"])
    ids_produtos = [produto["id"] for produto, _ in produtos]
    if len(ids_produtos) != len(set(ids_produtos)):
        raise QuantidadeExcedida("Cada produto pode ser incluído apenas uma vez na cesta.")
    if len(produtos) > limite:
        raise QuantidadeExcedida(
            f"A cesta {nome_tamanho(dados['tamanho'])} comporta até {limite} produtos diferentes."
        )
    for produto, quantidade in produtos:
        if quantidade > LIMITE_UNIDADES_POR_PRODUTO:
            raise QuantidadeExcedida(
                f"O produto {produto['nome']} permite até "
                f"{LIMITE_UNIDADES_POR_PRODUTO} unidades por cesta."
            )
        if quantidade > produto["estoque"]:
            raise EstoqueInsuficiente(
                f"Estoque insuficiente para {produto['nome']}. "
                f"Disponíveis: {produto['estoque']}."
            )
    semana = dados.get("semana") or date.today().isoformat()
    try:
        semana_convertida = date.fromisoformat(semana)
    except ValueError:
        raise SemanaInvalida("A semana deve estar no formato AAAA-MM-DD.")

    dados_cesta = {
        "assinante": usuario.usuario.strip().lower(),
        "semana": semana_convertida,
        "tamanho": normalizar_tamanho(dados["tamanho"]),
        "tamanho_nome": nome_tamanho(dados["tamanho"]),
        "modo": dados["modo"],
        "limite": limite,
        "situacao": "Pendente",
        "produtos": [
            {
                "id": produto["id"],
                "nome": produto["nome"],
                "quantidade": quantidade,
                "preco_unitario_centavos": produto["preco_centavos"],
            }
            for produto, quantidade in produtos
        ],
    }

    produto_esgotado = repositorio.reservar_estoque(
        sessao,
        [{"id": produto["id"], "quantidade": quantidade} for produto, quantidade in produtos],
    )
    if produto_esgotado is not None:
        produto = next(item for item, _ in produtos if item["id"] == produto_esgotado)
        raise EstoqueInsuficiente(
            f"O estoque de {produto['nome']} mudou. Atualize o catálogo e tente novamente."
        )

    try:
        cesta_criada = repositorio.adicionar_cesta(sessao, dados_cesta, usuario_id=usuario.id)
    except Exception:
        sessao.rollback()
        raise
    return serializar_cesta(cesta_criada)


def listar_separacoes(sessao: Session, id_cesta: int, usuario_id: int | None = None) -> list[dict]:
    """Retorna os produtos ja separados ou recusa uma cesta inexistente."""

    cesta = buscar_cesta(sessao, id_cesta, usuario_id=usuario_id)
    return cesta["separacoes"]


def separar_produto(
    sessao: Session,
    id_cesta: int,
    produto_id: str,
    quantidade: int,
    usuario_id: int | None = None,
) -> dict:
    """Registra a separacao respeitando o pedido e o limite da cesta."""

    cesta = buscar_cesta(sessao, id_cesta, usuario_id=usuario_id)
    if (
        cesta["separacao_concluida_em"] is not None
        or cesta["situacao"] in {"Entregue", "Cancelado"}
    ):
        raise QuantidadeExcedida("A cesta já está concluída e não pode ser alterada.")
    item_pedido = next((item for item in cesta["produtos"] if item["id"] == produto_id), None)
    if item_pedido is None:
        raise ProdutoNaoPertenceCesta("O produto não pertence a esta cesta.")

    separacao_existente = next(
        (item for item in cesta["separacoes"] if item["produto_id"] == produto_id), None
    )
    quantidade_atual_produto = separacao_existente["quantidade"] if separacao_existente else 0
    restante_produto = item_pedido["quantidade"] - quantidade_atual_produto

    if quantidade > restante_produto:
        raise QuantidadeExcedida(
            f"O produto {item_pedido['nome']} comporta mais {restante_produto} item(ns)."
        )

    if separacao_existente:
        separacao_existente["quantidade"] += quantidade
    else:
        cesta["separacoes"].append(
            {"produto_id": produto_id, "nome": item_pedido["nome"], "quantidade": quantidade}
        )

    cesta["situacao"] = "Em separação"

    return serializar_cesta(repositorio.atualizar_cesta(sessao, cesta))


def separar_produtos(
    sessao: Session,
    id_cesta: int,
    produtos: list[dict],
) -> dict:
    """Registra um lote completo após validar todas as quantidades."""

    cesta = buscar_cesta(sessao, id_cesta)
    if (
        cesta["separacao_concluida_em"] is not None
        or cesta["situacao"] in {"Entregue", "Cancelado"}
    ):
        raise QuantidadeExcedida("A cesta já está concluída e não pode ser alterada.")
    itens_pedido = {item["id"]: item for item in cesta["produtos"]}
    separacoes = {item["produto_id"]: item for item in cesta["separacoes"]}
    quantidades = {}

    for produto in produtos:
        produto_id = produto["produto_id"]
        if produto_id in quantidades:
            raise QuantidadeExcedida("O lote contém o mesmo produto mais de uma vez.")

        item_pedido = itens_pedido.get(produto_id)
        if item_pedido is None:
            raise ProdutoNaoPertenceCesta(f"O produto {produto_id} não pertence a esta cesta.")

        quantidade_atual = separacoes.get(produto_id, {}).get("quantidade", 0)
        if quantidade_atual + produto["quantidade"] > item_pedido["quantidade"]:
            restante = item_pedido["quantidade"] - quantidade_atual
            raise QuantidadeExcedida(
                f"O produto {item_pedido['nome']} comporta mais {restante} item(ns)."
            )

        quantidades[produto_id] = produto["quantidade"]

    for produto_id, quantidade in quantidades.items():
        if produto_id in separacoes:
            separacoes[produto_id]["quantidade"] += quantidade
        else:
            separacao = {
                "produto_id": produto_id,
                "nome": itens_pedido[produto_id]["nome"],
                "quantidade": quantidade,
            }
            cesta["separacoes"].append(separacao)
            separacoes[produto_id] = separacao

    cesta["situacao"] = "Em separação"

    return serializar_cesta(repositorio.atualizar_cesta(sessao, cesta))


def desfazer_separacoes(sessao: Session, id_cesta: int, produtos: list[dict]) -> dict:
    """Remove quantidades registradas, validando o lote antes de salvar."""

    cesta = buscar_cesta(sessao, id_cesta)
    if (
        cesta["separacao_concluida_em"] is not None
        or cesta["situacao"] in {"Entregue", "Cancelado"}
    ):
        raise QuantidadeExcedida("A cesta já está concluída e não pode ser alterada.")
    quantidades = {}

    for produto in produtos:
        produto_id = produto["produto_id"]
        if produto_id in quantidades:
            raise QuantidadeExcedida("O lote contém o mesmo produto mais de uma vez.")
        quantidades[produto_id] = produto["quantidade"]

    existentes = {item["produto_id"]: item for item in cesta["separacoes"]}
    for produto_id, quantidade in quantidades.items():
        separacao = existentes.get(produto_id)
        if separacao is None or quantidade > separacao["quantidade"]:
            raise QuantidadeExcedida(
                f"Não é possível desfazer {quantidade} item(ns) de {produto_id}."
            )

    cesta["separacoes"] = [
        {
            **separacao,
            "quantidade": separacao["quantidade"] - quantidades.get(separacao["produto_id"], 0),
        }
        for separacao in cesta["separacoes"]
        if separacao["quantidade"] - quantidades.get(separacao["produto_id"], 0) > 0
    ]

    cesta["situacao"] = "Em separação" if cesta["separacoes"] else "Pendente"

    return serializar_cesta(repositorio.atualizar_cesta(sessao, cesta))


def concluir_separacao(sessao: Session, id_cesta: int) -> dict:
    """Conclui a cesta somente quando todas as quantidades pedidas foram separadas."""

    cesta = buscar_cesta(sessao, id_cesta)
    if cesta["situacao"] == "Cancelado":
        raise QuantidadeExcedida("Uma cesta cancelada não pode ser concluída.")
    separacoes = {item["produto_id"]: item["quantidade"] for item in cesta["separacoes"]}
    pendentes = [
        f"{produto['nome']} ({separacoes.get(produto['id'], 0)} de {produto['quantidade']})"
        for produto in cesta["produtos"]
        if separacoes.get(produto["id"], 0) < produto["quantidade"]
    ]

    if pendentes:
        raise QuantidadeExcedida(
            f"Não é possível concluir. Ainda falta separar: {', '.join(pendentes)}."
        )

    if cesta["separacao_concluida_em"] is not None:
        raise QuantidadeExcedida("A separação desta cesta já foi concluída.")

    cesta["situacao"] = "Preparado para envio"
    cesta["separacao_concluida_em"] = datetime.now(timezone.utc)
    return serializar_cesta(repositorio.atualizar_cesta(sessao, cesta))


def salvar_separacao(sessao: Session, id_cesta: int, produtos: list[dict]) -> dict:
    """Substitui as quantidades conferidas e conclui somente se o pedido estiver completo."""

    cesta = buscar_cesta(sessao, id_cesta)
    if cesta["situacao"] in {"Entregue", "Cancelado"}:
        raise QuantidadeExcedida("Uma cesta entregue ou cancelada não pode ser alterada.")
    if cesta["separacao_concluida_em"] is not None:
        raise QuantidadeExcedida("Reabra a separação antes de corrigir as quantidades.")

    itens_pedido = {item["id"]: item for item in cesta["produtos"]}
    quantidades = _validar_quantidades_conferidas(itens_pedido, produtos)

    cesta["separacoes"] = [
        {"produto_id": produto_id, "nome": itens_pedido[produto_id]["nome"], "quantidade": quantidade}
        for produto_id, quantidade in quantidades.items()
        if quantidade > 0
    ]
    completa = all(quantidades[item["id"]] == item["quantidade"] for item in cesta["produtos"])
    cesta["separacao_concluida_em"] = datetime.now(timezone.utc) if completa else None
    cesta["situacao"] = (
        "Preparado para envio" if completa else
        "Em separação" if cesta["separacoes"] else "Pendente"
    )
    return serializar_cesta(repositorio.atualizar_cesta(sessao, cesta))


def _validar_quantidades_conferidas(itens_pedido: dict, produtos: list[dict]) -> dict[str, int]:
    quantidades = {}
    for produto in produtos:
        produto_id = produto["produto_id"]
        if produto_id in quantidades:
            raise QuantidadeExcedida("O produto foi informado mais de uma vez.")
        item = itens_pedido.get(produto_id)
        if item is None:
            raise ProdutoNaoPertenceCesta(f"O produto {produto_id} não pertence a esta cesta.")
        if produto["quantidade"] > item["quantidade"]:
            raise QuantidadeExcedida(f"A quantidade de {item['nome']} ultrapassa o pedido.")
        quantidades[produto_id] = produto["quantidade"]

    if set(quantidades) != set(itens_pedido):
        raise QuantidadeExcedida("Informe a quantidade conferida de todos os produtos da cesta.")
    return quantidades


def encerrar_separacao_com_faltantes(sessao: Session, id_cesta: int, produtos: list[dict]) -> dict:
    """Finaliza com as quantidades reais, reduz o valor e devolve ao estoque o que faltou."""

    cesta = buscar_cesta(sessao, id_cesta)
    if cesta["situacao"] in {"Enviado", "Entregue", "Cancelado"}:
        raise QuantidadeExcedida("Um pedido enviado, entregue ou cancelado não pode ser ajustado.")
    if cesta["separacao_concluida_em"] is not None:
        raise QuantidadeExcedida("A separação deste pedido já foi encerrada.")

    itens_pedido = {item["id"]: item for item in cesta["produtos"]}
    quantidades = _validar_quantidades_conferidas(itens_pedido, produtos)
    if not any(quantidades.values()):
        raise QuantidadeExcedida("Separe ao menos um item antes de encerrar o pedido com faltantes.")

    faltantes = [
        {"id": produto_id, "quantidade": item["quantidade"] - quantidades[produto_id]}
        for produto_id, item in itens_pedido.items()
        if quantidades[produto_id] < item["quantidade"]
    ]
    if not faltantes:
        raise QuantidadeExcedida("Todos os itens foram separados. Use o fechamento normal do pedido.")

    cesta["separacoes"] = [
        {"produto_id": produto_id, "nome": itens_pedido[produto_id]["nome"], "quantidade": quantidade}
        for produto_id, quantidade in quantidades.items()
        if quantidade > 0
    ]
    repositorio.devolver_estoque(sessao, faltantes)
    cesta["separacao_concluida_em"] = datetime.now(timezone.utc)
    cesta["situacao"] = "Preparado para envio"
    return serializar_cesta(repositorio.atualizar_cesta(sessao, cesta))


def reabrir_separacao(sessao: Session, id_cesta: int) -> dict:
    """Reabre uma separação concluída para permitir correções antes da entrega."""

    cesta = buscar_cesta(sessao, id_cesta)
    if cesta["situacao"] in {"Enviado", "Entregue", "Cancelado"}:
        raise QuantidadeExcedida("Uma cesta enviada, entregue ou cancelada não pode ser reaberta.")
    if cesta["separacao_concluida_em"] is None:
        raise QuantidadeExcedida("A separação desta cesta ainda não foi concluída.")

    separacoes = {item["produto_id"]: item["quantidade"] for item in cesta["separacoes"]}
    faltantes_reservados = [
        {"id": produto["id"], "quantidade": produto["quantidade"] - separacoes.get(produto["id"], 0)}
        for produto in cesta["produtos"]
        if (produto["quantidade"] - separacoes.get(produto["id"], 0)) > 0
    ]
    if faltantes_reservados:
        produto_sem_estoque = repositorio.reservar_estoque(sessao, faltantes_reservados)
        if produto_sem_estoque:
            raise EstoqueInsuficiente(
                f"Não há estoque suficiente de {produto_sem_estoque} para reabrir o pedido."
            )

    cesta["separacao_concluida_em"] = None
    cesta["situacao"] = "Em separação" if cesta["separacoes"] else "Pendente"
    return serializar_cesta(repositorio.atualizar_cesta(sessao, cesta))


def cancelar_cesta(sessao: Session, id_cesta: int, usuario_id: int) -> dict:
    """Cancela a cesta da assinante somente antes do início da separação."""

    cesta = buscar_cesta(sessao, id_cesta, usuario_id=usuario_id)
    if cesta["situacao"] == "Cancelado":
        return cesta
    if cesta["situacao"] != "Pendente" or cesta["separacoes"]:
        raise QuantidadeExcedida(
            "Só é possível cancelar o pedido enquanto ele estiver pendente."
        )

    cesta["situacao"] = "Cancelado"
    repositorio.devolver_estoque(sessao, cesta["produtos"])
    return serializar_cesta(repositorio.atualizar_cesta(sessao, cesta))


def confirmar_entrega(sessao: Session, id_cesta: int, usuario_id: int) -> dict:
    """Confirma que a assinante recebeu uma cesta com separação concluída."""

    cesta = buscar_cesta(sessao, id_cesta, usuario_id=usuario_id)
    if cesta["situacao"] == "Entregue":
        return cesta
    if cesta.get("situacao") != "Enviado" or cesta.get("enviado_em") is None:
        raise QuantidadeExcedida(
            "O recebimento só pode ser confirmado depois que o produtor marcar o pedido como enviado."
        )

    cesta["situacao"] = "Entregue"
    return serializar_cesta(repositorio.atualizar_cesta(sessao, cesta))


def marcar_enviado(sessao: Session, id_cesta: int) -> dict:
    """Marca a cesta preparada como enviada e registra aviso persistente ao cliente."""

    cesta = buscar_cesta(sessao, id_cesta)
    if cesta.get("situacao") == "Enviado":
        return cesta
    if cesta.get("situacao") != "Preparado para envio" or not cesta.get("separacao_concluida_em"):
        raise QuantidadeExcedida("Conclua a separação antes de marcar o pedido como enviado.")

    cesta["situacao"] = "Enviado"
    cesta["enviado_em"] = datetime.now(timezone.utc)
    cliente = sessao.scalar(
        select(Usuario).where(func.lower(Usuario.usuario) == cesta["assinante"].strip().lower())
    )
    usuario_id = cliente.id if cliente else None
    if usuario_id is not None:
        sessao.add(Notificacao(
            usuario_id=usuario_id,
            cesta_id=id_cesta,
            titulo="Pedido enviado",
            mensagem=f"Seu pedido #{id_cesta:04d} foi marcado como enviado pelo produtor.",
            criada_em=datetime.now(timezone.utc),
            lida=False,
        ))

    cesta_atualizada = repositorio.atualizar_cesta(sessao, cesta)
    return serializar_cesta(cesta_atualizada)


def avaliar_cesta(sessao: Session, id_cesta: int, usuario: Usuario, estrelas: int) -> dict:
    """Registra a nota do assinante ou do produtor após a entrega."""

    usuario_id = usuario.id if usuario.perfil == "assinante" else None
    cesta = repositorio.buscar_cesta_por_id(sessao, id_cesta, usuario_id=usuario_id)
    if cesta is None:
        raise CestaNaoEncontrada("Cesta não encontrada.")
    if cesta["situacao"] != "Entregue":
        raise AvaliacaoInvalida("A avaliação só pode ser registrada após a entrega.")

    campo = "avaliacao_assinante" if usuario.perfil == "assinante" else "avaliacao_produtor"
    if cesta[campo] is not None:
        raise AvaliacaoInvalida("Esta pessoa já avaliou este pedido.")

    resultado = repositorio.registrar_avaliacao(sessao, id_cesta, campo, estrelas)
    if resultado is None:
        raise CestaNaoEncontrada("Cesta não encontrada.")
    return serializar_cesta(resultado)
