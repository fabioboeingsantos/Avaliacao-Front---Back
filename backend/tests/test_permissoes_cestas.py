"""Testes de propriedade das cestas e permissoes por perfil."""

from datetime import datetime, timedelta, timezone

from modelos.cesta import Cesta

from .conftest import SessaoDeTeste, fazer_login


def test_assinante_ve_somente_as_proprias_cestas(cliente):
    """A consulta do assinante e filtrada pelo usuario do token."""

    token = fazer_login(cliente, "aline", "aline123")
    resposta = cliente.get("/cestas", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["assinante"] == "aline"


def test_assinante_nao_acessa_cesta_de_outro_usuario(cliente):
    """Um id valido de outra conta se comporta como nao encontrado."""

    token_produtor = fazer_login(cliente, "vanderlei", "vanderlei123")
    cestas = cliente.get(
        "/cestas",
        headers={"Authorization": f"Bearer {token_produtor}"},
    ).json()
    cesta_de_outro_usuario = next(cesta for cesta in cestas if cesta["assinante"] == "vanderlei")

    token = fazer_login(cliente, "aline", "aline123")
    resposta = cliente.get(
        f"/cestas/{cesta_de_outro_usuario['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 404


def test_assinante_nao_pode_registrar_separacao(cliente):
    """A separacao e uma operacao exclusiva do perfil produtor."""

    token = fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post(
        "/cestas/1/separacoes",
        headers={"Authorization": f"Bearer {token}"},
        json={"produto_id": "alface", "quantidade": 1},
    )

    assert resposta.status_code == 403


def test_assinante_pode_cancelar_proprio_pedido_pendente(cliente):
    """A assinante cancela uma cesta antes de o produtor iniciar a separação."""

    fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post("/cestas/1/cancelar")

    assert resposta.status_code == 200
    assert resposta.json()["situacao"] == "Cancelado"
    assert cliente.get("/cestas/1").json()["situacao"] == "Cancelado"


def test_assinante_nao_pode_cancelar_pedido_de_outra_conta(cliente):
    """O cancelamento respeita o vínculo da cesta com a conta autenticada."""

    fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post("/cestas/2/cancelar")

    assert resposta.status_code == 404


def test_assinante_nao_pode_cancelar_pedido_em_separacao(cliente):
    """A cesta não pode ser cancelada depois que o produtor começar a separação."""

    fazer_login(cliente, "vanderlei", "vanderlei123")
    cliente.post(
        "/cestas/1/separacoes",
        json={"produto_id": "alface", "quantidade": 1},
    )

    fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post("/cestas/1/cancelar")

    assert resposta.status_code == 422
    assert cliente.get("/cestas/1").json()["situacao"] == "Em separação"


def test_produtor_nao_pode_cancelar_pedido(cliente):
    """O cancelamento é uma ação exclusiva da assinante."""

    fazer_login(cliente, "vanderlei", "vanderlei123")
    resposta = cliente.post("/cestas/1/cancelar")

    assert resposta.status_code == 403


def test_produtor_nao_pode_separar_pedido_cancelado(cliente):
    """Pedidos cancelados não podem voltar para o fluxo de separação."""

    fazer_login(cliente, "aline", "aline123")
    cliente.post("/cestas/1/cancelar")

    fazer_login(cliente, "vanderlei", "vanderlei123")
    resposta = cliente.post(
        "/cestas/1/separacoes",
        json={"produto_id": "alface", "quantidade": 1},
    )

    assert resposta.status_code == 422
    assert cliente.get("/cestas/1").json()["situacao"] == "Cancelado"


def test_produtor_pode_registrar_separacao(cliente):
    """O produtor autenticado pode atualizar uma cesta existente."""

    token = fazer_login(cliente, "vanderlei", "vanderlei123")
    resposta = cliente.post(
        "/cestas/1/separacoes",
        headers={"Authorization": f"Bearer {token}"},
        json={"produto_id": "alface", "quantidade": 1},
    )

    assert resposta.status_code == 200
    assert resposta.json()["separacoes"][0]["quantidade"] == 1


def test_produtor_pode_registrar_lote_de_separacoes(cliente):
    """O produtor registra a cesta em lote e recebe as quantidades atualizadas."""

    token = fazer_login(cliente, "vanderlei", "vanderlei123")
    resposta = cliente.post(
        "/cestas/1/separacoes/lote",
        headers={"Authorization": f"Bearer {token}"},
        json={"produtos": [{"produto_id": "alface", "quantidade": 2}]},
    )

    assert resposta.status_code == 200
    assert resposta.json()["separacoes"][0]["quantidade"] == 2
    assert resposta.json()["situacao"] == "Em separação"


def test_produtor_conclui_separacao_depois_de_separar_todos_os_itens(cliente):
    """A conclusão da separação inicia o prazo de confirmação do recebimento."""

    token = fazer_login(cliente, "vanderlei", "vanderlei123")
    headers = {"Authorization": f"Bearer {token}"}
    cliente.post(
        "/cestas/1/separacoes/lote",
        headers=headers,
        json={"produtos": [{"produto_id": "alface", "quantidade": 2}]},
    )

    resposta = cliente.post("/cestas/1/separacoes/concluir", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["situacao"] == "Em separação"
    assert resposta.json()["separacao_concluida_em"] is not None


def test_produtor_nao_conclui_cesta_com_produtos_pendentes(cliente):
    """A API impede concluir enquanto ainda houver produtos não separados."""

    token = fazer_login(cliente, "vanderlei", "vanderlei123")
    resposta = cliente.post(
        "/cestas/1/separacoes/concluir",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 422
    assert "Alface" in resposta.json()["detail"]


def test_assinante_nao_pode_concluir_separacao(cliente):
    """Somente o produtor pode concluir a separação de uma cesta."""

    token = fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post(
        "/cestas/1/separacoes/concluir",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 403


def test_assinante_pode_confirmar_recebimento_da_cesta(cliente):
    """A assinante confirma o recebimento depois da separacao concluida."""

    fazer_login(cliente, "vanderlei", "vanderlei123")
    cliente.post(
        "/cestas/1/separacoes/lote",
        json={"produtos": [{"produto_id": "alface", "quantidade": 2}]},
    )
    cliente.post("/cestas/1/separacoes/concluir")

    fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post("/cestas/1/entrega/confirmar")

    assert resposta.status_code == 200
    assert resposta.json()["situacao"] == "Entregue"
    assert resposta.json()["produtos"][0]["quantidade"] == 2
    assert resposta.json()["separacoes"][0]["quantidade"] == 2


def test_assinante_nao_confirma_entrega_antes_da_conclusao_da_separacao(cliente):
    """O recebimento so pode ser confirmado apos a separacao terminar."""

    fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post("/cestas/1/entrega/confirmar")

    assert resposta.status_code == 422
    assert resposta.json()["detail"].startswith("A entrega")


def test_assinante_nao_confirma_entrega_de_cesta_de_outra_conta(cliente):
    """A assinante so pode confirmar cestas vinculadas a sua propria conta."""

    fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post("/cestas/2/entrega/confirmar")

    assert resposta.status_code == 404


def test_assinante_e_produtor_avaliam_pedido_entregue(cliente):
    """Cada perfil registra sua própria nota de zero a cinco estrelas."""

    fazer_login(cliente, "vanderlei", "vanderlei123")
    cliente.post(
        "/cestas/1/separacoes/lote",
        json={"produtos": [{"produto_id": "alface", "quantidade": 2}]},
    )
    cliente.post("/cestas/1/separacoes/concluir")

    fazer_login(cliente, "aline", "aline123")
    cliente.post("/cestas/1/entrega/confirmar")
    nota_assinante = cliente.post("/cestas/1/avaliacao", json={"estrelas": 5})

    assert nota_assinante.status_code == 200
    assert nota_assinante.json()["avaliacao_assinante"] == 5
    assert nota_assinante.json()["avaliacao_produtor"] is None

    fazer_login(cliente, "vanderlei", "vanderlei123")
    nota_produtor = cliente.post("/cestas/1/avaliacao", json={"estrelas": 0})

    assert nota_produtor.status_code == 200
    assert nota_produtor.json()["avaliacao_assinante"] == 5
    assert nota_produtor.json()["avaliacao_produtor"] == 0


def test_avaliacao_so_pode_ser_registrada_uma_vez_por_perfil(cliente):
    """Uma mesma pessoa não substitui a nota já gravada no pedido."""

    fazer_login(cliente, "vanderlei", "vanderlei123")
    cliente.post(
        "/cestas/1/separacoes/lote",
        json={"produtos": [{"produto_id": "alface", "quantidade": 2}]},
    )
    cliente.post("/cestas/1/separacoes/concluir")
    fazer_login(cliente, "aline", "aline123")
    cliente.post("/cestas/1/entrega/confirmar")
    cliente.post("/cestas/1/avaliacao", json={"estrelas": 3})

    repetida = cliente.post("/cestas/1/avaliacao", json={"estrelas": 4})

    assert repetida.status_code == 422
    assert "já avaliou" in repetida.json()["detail"]


def test_avaliacao_rejeita_nota_fora_do_intervalo(cliente):
    """O schema impede valores menores que zero ou maiores que cinco."""

    fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post("/cestas/1/avaliacao", json={"estrelas": 6})

    assert resposta.status_code == 422


def test_produtor_nao_pode_confirmar_entrega(cliente):
    """A confirmação de recebimento é uma ação exclusiva da assinante."""

    fazer_login(cliente, "vanderlei", "vanderlei123")
    resposta = cliente.post("/cestas/1/entrega/confirmar")

    assert resposta.status_code == 403


def test_cesta_expira_para_entregue_sete_dias_apos_conclusao(cliente):
    """A primeira consulta apos sete dias atualiza a situacao para entregue."""

    fazer_login(cliente, "vanderlei", "vanderlei123")
    cliente.post(
        "/cestas/1/separacoes/lote",
        json={"produtos": [{"produto_id": "alface", "quantidade": 2}]},
    )
    cliente.post("/cestas/1/separacoes/concluir")

    sessao = SessaoDeTeste()
    cesta = sessao.get(Cesta, 1)
    cesta.separacao_concluida_em = datetime.now(timezone.utc) - timedelta(days=7, seconds=1)
    sessao.commit()
    sessao.close()

    fazer_login(cliente, "aline", "aline123")
    resposta = cliente.get("/cestas/1")

    assert resposta.status_code == 200
    assert resposta.json()["situacao"] == "Entregue"


def test_lote_invalido_nao_registra_parcialmente(cliente):
    """Produto inválido rejeita o lote sem salvar os itens válidos anteriores."""

    token = fazer_login(cliente, "vanderlei", "vanderlei123")
    headers = {"Authorization": f"Bearer {token}"}
    resposta = cliente.post(
        "/cestas/1/separacoes/lote",
        headers=headers,
        json={
            "produtos": [
                {"produto_id": "alface", "quantidade": 1},
                {"produto_id": "nao-existe", "quantidade": 1},
            ]
        },
    )
    cesta = cliente.get("/cestas/1", headers=headers).json()

    assert resposta.status_code == 422
    assert cesta["separacoes"] == []
    assert cesta["situacao"] == "Pendente"


def test_produtor_pode_desfazer_lote_de_separacoes(cliente):
    """Desfazer o lote restaura quantidades e situação anterior da cesta."""

    token = fazer_login(cliente, "vanderlei", "vanderlei123")
    headers = {"Authorization": f"Bearer {token}"}
    cliente.post(
        "/cestas/1/separacoes",
        headers=headers,
        json={"produto_id": "alface", "quantidade": 1},
    )

    resposta = cliente.post(
        "/cestas/1/separacoes/desfazer",
        headers=headers,
        json={"produtos": [{"produto_id": "alface", "quantidade": 1}]},
    )

    assert resposta.status_code == 200
    assert resposta.json()["separacoes"] == []
    assert resposta.json()["situacao"] == "Pendente"


def test_desfazer_lote_invalido_nao_altera_separacoes(cliente):
    """Um desfazer inválido não aplica parcialmente o lote."""

    token = fazer_login(cliente, "vanderlei", "vanderlei123")
    headers = {"Authorization": f"Bearer {token}"}
    cliente.post(
        "/cestas/1/separacoes",
        headers=headers,
        json={"produto_id": "alface", "quantidade": 1},
    )

    resposta = cliente.post(
        "/cestas/1/separacoes/desfazer",
        headers=headers,
        json={
            "produtos": [
                {"produto_id": "alface", "quantidade": 1},
                {"produto_id": "alface", "quantidade": 1},
            ]
        },
    )
    cesta = cliente.get("/cestas/1", headers=headers).json()

    assert resposta.status_code == 422
    assert cesta["separacoes"][0]["quantidade"] == 1


def test_assinante_nao_pode_desfazer_separacao(cliente):
    """Desfazer separações é uma operação exclusiva do produtor."""

    token = fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post(
        "/cestas/1/separacoes/desfazer",
        headers={"Authorization": f"Bearer {token}"},
        json={"produtos": [{"produto_id": "alface", "quantidade": 1}]},
    )

    assert resposta.status_code == 403


def test_criacao_usa_o_usuario_do_token(cliente):
    """O cliente nao consegue criar uma cesta em nome de outra conta."""

    token = fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post(
        "/cestas",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "assinante": "vanderlei",
            "usuario_id": 2,
            "tamanho": "pequena",
            "modo": "pronta",
            "produtos": [{"id": "alface", "nome": "Alface", "quantidade": 1}],
        },
    )

    assert resposta.status_code == 201
    assert resposta.json()["assinante"] == "aline"
    assert resposta.json()["situacao"] == "Pendente"


def test_assinante_pode_pedir_ate_dez_unidades_de_um_produto(cliente):
    """O limite de produtos diferentes não impede dez unidades de um produto."""

    token = fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post(
        "/cestas",
        headers={"Authorization": f"******"},
        json={
            "tamanho": "pequena",
            "modo": "selecionavel",
            "produtos": [{"id": "alface", "nome": "Alface", "quantidade": 10}],
        },
    )

    assert resposta.status_code == 201
    assert resposta.json()["produtos"][0]["quantidade"] == 10


def test_cesta_calcula_preco_unitario_subtotal_e_total(cliente):
    """O pedido calcula o valor por unidade e preserva o total pela quantidade."""

    # O fixture usa o preço padrão de R$ 5,00 para o produto de teste.
    fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post(
        "/cestas",
        json={
            "tamanho": "pequena",
            "modo": "selecionavel",
            "produtos": [{"id": "alface", "nome": "Alface", "quantidade": 2}],
        },
    )

    # Duas unidades de R$ 5,00 devem resultar em subtotal e total de R$ 10,00.
    assert resposta.status_code == 201
    produto = resposta.json()["produtos"][0]
    assert produto["preco_unitario"] == 5
    assert produto["subtotal"] == 10
    assert resposta.json()["valor_total"] == 10


def test_produtor_pode_atualizar_preco_unitario(cliente):
    """Somente o produtor atualiza o preço, e o catálogo devolve o novo valor."""

    # A alteração é feita pela rota protegida do catálogo de produtos.
    fazer_login(cliente, "vanderlei", "vanderlei123")
    resposta = cliente.put("/produtos/alface/preco", json={"preco_unitario": 1.25})

    # O preço retorna em reais, embora o banco armazene centavos.
    assert resposta.status_code == 200
    assert resposta.json()["preco_unitario"] == 1.25
    produtos = cliente.get("/produtos").json()
    produto = next(item for item in produtos if item["id"] == "alface")
    assert produto["preco_unitario"] == 1.25


def test_assinante_pode_pedir_dez_unidades_de_cinco_produtos_em_cesta_pequena(cliente):
    """Pequena limita cinco produtos distintos, não o total de unidades."""

    fazer_login(cliente, "aline", "aline123")
    produtos = [
        {"id": produto_id, "nome": produto_id.title(), "quantidade": 10}
        for produto_id in ("alface", "tomate", "cenoura", "batata", "cebola")
    ]
    resposta = cliente.post(
        "/cestas",
        json={"tamanho": "pequena", "modo": "selecionavel", "produtos": produtos},
    )

    assert resposta.status_code == 201
    assert len(resposta.json()["produtos"]) == 5
    assert sum(produto["quantidade"] for produto in resposta.json()["produtos"]) == 50


def test_assinante_nao_pode_escolher_mais_produtos_que_o_tamanho(cliente):
    """O limite Pequena rejeita um sexto produto, mesmo com uma unidade."""

    fazer_login(cliente, "aline", "aline123")
    produtos = [
        {"id": produto_id, "nome": produto_id.title(), "quantidade": 1}
        for produto_id in ("alface", "tomate", "cenoura", "batata", "cebola", "couve")
    ]
    resposta = cliente.post(
        "/cestas",
        json={"tamanho": "pequena", "modo": "selecionavel", "produtos": produtos},
    )

    assert resposta.status_code == 422
    assert "5 produtos diferentes" in resposta.json()["detail"]


def test_produtor_pode_registrar_todas_as_unidades_pedidas(cliente):
    """A separação não aplica o limite de produtos distintos ao total de unidades."""

    fazer_login(cliente, "aline", "aline123")
    cesta = cliente.post(
        "/cestas",
        json={
            "tamanho": "pequena",
            "modo": "selecionavel",
            "produtos": [{"id": "alface", "nome": "Alface", "quantidade": 10}],
        },
    ).json()

    fazer_login(cliente, "vanderlei", "vanderlei123")
    resposta = cliente.post(
        f"/cestas/{cesta['id']}/separacoes/lote",
        json={"produtos": [{"produto_id": "alface", "quantidade": 10}]},
    )

    assert resposta.status_code == 200
    assert resposta.json()["separacoes"][0]["quantidade"] == 10


def test_assinante_nao_pode_pedir_mais_de_dez_unidades_de_um_produto(cliente):
    """A API rejeita quantidades acima do limite por produto."""

    token = fazer_login(cliente, "aline", "aline123")
    resposta = cliente.post(
        "/cestas",
        headers={"Authorization": f"******"},
        json={
            "tamanho": "grande",
            "modo": "selecionavel",
            "produtos": [{"id": "alface", "nome": "Alface", "quantidade": 11}],
        },
    )

    assert resposta.status_code == 422


def test_produtor_nao_pode_criar_cesta(cliente):
    """O grupo produtor nao possui a permissao de criar cestas."""

    token = fazer_login(cliente, "vanderlei", "vanderlei123")
    resposta = cliente.post(
        "/cestas",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "tamanho": "pequena",
            "modo": "pronta",
            "produtos": [{"id": "alface", "nome": "Alface", "quantidade": 1}],
        },
    )

    assert resposta.status_code == 403
