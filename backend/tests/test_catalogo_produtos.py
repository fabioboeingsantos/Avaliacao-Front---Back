"""Cadastro de produtos e integração com catálogo, estoque e Flora."""

import pytest
from .conftest import fazer_login


NOVO = {"nome": "Banana", "categoria": "frutas", "estoque": 8, "preco_unitario": 1.75}


def test_somente_produtor_pode_cadastrar(cliente):
    assert cliente.post('/produtos', json=NOVO).status_code == 401
    fazer_login(cliente, 'aline', 'aline123')
    assert cliente.post('/produtos', json=NOVO).status_code == 403
    fazer_login(cliente, 'vanderlei', 'vanderlei123')
    resposta = cliente.post('/produtos', json=NOVO)
    assert resposta.status_code == 201
    assert resposta.json() == {"id": "banana", **NOVO}
    assert cliente.post('/produtos', json={**NOVO, 'nome': ' BÁNANA '}).status_code == 409
    assert len([p for p in cliente.get('/produtos').json() if p['id'] == 'banana']) == 1
    fazer_login(cliente, 'aline', 'aline123')
    catalogo = cliente.post('/assistente/analisar', json={'mensagem': 'Quais frutas temos?'}).json()
    assert 'Banana' in catalogo['mensagem']
    proposta = cliente.post('/assistente/analisar', json={'mensagem': 'Quero uma cesta pequena com 2 bananas'}).json()
    assert proposta['status'] == 'proposta'
    assert proposta['proposta']['produtos'][0]['produto_id'] == 'banana'
    pedido = cliente.post('/cestas', json={'tamanho': 'pequena', 'modo': 'selecionavel',
                                         'produtos': [{'id': 'banana', 'nome': 'Banana', 'quantidade': 2}]})
    assert pedido.status_code == 201
    assert pedido.json()['valor_total'] == 3.5


@pytest.mark.parametrize('alteracoes', [
    {'nome': '   '}, {'nome': 'A'}, {'categoria': 'outra'}, {'estoque': -1},
    {'estoque': 1.5}, {'preco_unitario': 0}, {'preco_unitario': 1.755}, {'id': 'forjado'},
])
def test_cadastro_rejeita_dados_invalidos(cliente, alteracoes):
    fazer_login(cliente, 'vanderlei', 'vanderlei123')
    assert cliente.post('/produtos', json={**NOVO, **alteracoes}).status_code == 422


def test_produto_sem_estoque_nao_e_recomendado(cliente):
    fazer_login(cliente, 'vanderlei', 'vanderlei123')
    assert cliente.post('/produtos', json={**NOVO, 'estoque': 0}).status_code == 201
    fazer_login(cliente, 'aline', 'aline123')
    dados = cliente.post('/assistente/analisar', json={'mensagem': 'Mostrar catálogo completo'}).json()
    assert 'Banana' not in dados['mensagem']
    sugestao = cliente.post('/assistente/analisar', json={'mensagem': 'Recomende uma cesta pequena de frutas'}).json()
    assert sugestao['status'] != 'proposta'
