"""Fluxos completos com SQLite isolado e entrega SMTP interceptada."""

from datetime import timedelta
from hashlib import sha256
import pytest
from sqlalchemy import select
from modelos.token_conta import TokenConta
from modelos.usuario import Usuario
from servicos import email_conta, tokens_conta
from .conftest import SessaoDeTeste, fazer_login


@pytest.fixture
def emails(cliente, monkeypatch):
    mensagens = []
    monkeypatch.setattr(email_conta, 'enviar', lambda *args: mensagens.append(args))
    return mensagens


def cadastrar(cliente):
    return cliente.post('/usuarios', json={
        'usuario': 'nova', 'email': 'nova@example.com', 'senha': 'senha-segura'})


def token_email(emails):
    return emails[-1][2].split('=', 1)[1].split()[0]


def test_cadastro_confirmacao_login_e_uso_unico(cliente, emails):
    resposta = cadastrar(cliente)
    assert resposta.status_code == 201
    assert resposta.json()['email_verificado'] is False
    token = token_email(emails)
    with SessaoDeTeste() as sessao:
        registro = sessao.scalar(select(TokenConta))
        assert registro.token_hash == sha256(token.encode()).hexdigest()
        assert token not in registro.token_hash
    login = {'usuario': 'nova', 'senha': 'senha-segura'}
    assert cliente.post('/autenticacao/login', json=login).status_code == 403
    assert cliente.post('/autenticacao/verificar-email', json={'token': token}).status_code == 200
    assert cliente.post('/autenticacao/verificar-email', json={'token': token}).status_code == 400
    assert cliente.post('/autenticacao/login', json=login).status_code == 200


def test_reenvio_invalida_link_anterior(cliente, emails):
    cadastrar(cliente)
    antigo = token_email(emails)
    assert cliente.post('/autenticacao/reenviar-confirmacao', json={'email': 'nova@example.com'}).status_code == 202
    novo = token_email(emails)
    assert novo != antigo
    assert cliente.post('/autenticacao/verificar-email', json={'token': antigo}).status_code == 400
    assert cliente.post('/autenticacao/verificar-email', json={'token': novo}).status_code == 200


@pytest.mark.parametrize('rota', ['solicitar-recuperacao', 'reenviar-confirmacao'])
def test_resposta_nao_revela_conta(cliente, emails, rota):
    cadastrar(cliente)
    conhecida = cliente.post(f'/autenticacao/{rota}', json={'email': 'nova@example.com'})
    quantidade = len(emails)
    desconhecida = cliente.post(f'/autenticacao/{rota}', json={'email': 'ninguem@example.com'})
    assert conhecida.status_code == desconhecida.status_code == 202
    assert conhecida.json() == desconhecida.json()
    assert len(emails) == quantidade


def test_reset_troca_senha_revoga_sessoes_e_nao_reutiliza(cliente, emails):
    # Conta verificada com e-mail válido para solicitar recuperação.
    with SessaoDeTeste() as sessao:
        conta = sessao.scalar(select(Usuario).where(Usuario.usuario == 'aline'))
        conta.email = 'aline@example.com'
        sessao.commit()
    jwt_antigo = fazer_login(cliente, 'aline', 'aline123')
    assert cliente.post('/autenticacao/solicitar-recuperacao', json={'email': 'aline@example.com'}).status_code == 202
    token = token_email(emails)
    assert cliente.post('/autenticacao/redefinir-senha', json={'token': token, 'senha': 'minha-nova-senha'}).status_code == 200
    assert cliente.get('/usuarios/me', headers={'Authorization': f'Bearer {jwt_antigo}'}).status_code == 401
    assert cliente.post('/autenticacao/redefinir-senha', json={'token': token, 'senha': 'outra-senha-segura'}).status_code == 400
    assert cliente.post('/autenticacao/login', json={'usuario': 'aline', 'senha': 'aline123'}).status_code == 401
    assert cliente.post('/autenticacao/login', json={'usuario': 'aline', 'senha': 'minha-nova-senha'}).status_code == 200
    assert emails[-1][1].endswith('Senha alterada')


@pytest.mark.parametrize('expirado', [True, False])
def test_recusa_token_expirado_ou_falso(cliente, emails, expirado):
    cadastrar(cliente)
    token = token_email(emails) if expirado else 'x' * 43
    if expirado:
        with SessaoDeTeste() as sessao:
            registro = sessao.scalar(select(TokenConta))
            registro.expira_em = tokens_conta.agora() - timedelta(seconds=1)
            sessao.commit()
    assert cliente.post('/autenticacao/verificar-email', json={'token': token}).status_code == 400


def test_token_confirmacao_nao_redefine_senha(cliente, emails):
    cadastrar(cliente)
    token = token_email(emails)
    assert cliente.post('/autenticacao/redefinir-senha', json={'token': token, 'senha': 'senha-diferente'}).status_code == 400
    assert cliente.post('/autenticacao/verificar-email', json={'token': token}).status_code == 200


def test_limita_reenvio_por_email(cliente, emails):
    for _ in range(3):
        assert cliente.post('/autenticacao/reenviar-confirmacao', json={'email': 'ninguem@example.com'}).status_code == 202
    resposta = cliente.post('/autenticacao/reenviar-confirmacao', json={'email': 'ninguem@example.com'})
    assert resposta.status_code == 429
    assert 'retry-after' in resposta.headers


def test_reset_rejeita_senha_curta_sem_consumir_token(cliente, emails):
    cadastrar(cliente)
    cliente.post('/autenticacao/solicitar-recuperacao', json={'email': 'nova@example.com'})
    token = token_email(emails)
    assert cliente.post('/autenticacao/redefinir-senha', json={'token': token, 'senha': 'curta'}).status_code == 422
    assert cliente.post('/autenticacao/redefinir-senha', json={'token': token, 'senha': 'senha-valida-nova'}).status_code == 200
    assert cliente.post('/autenticacao/login', json={'usuario': 'nova', 'senha': 'senha-valida-nova'}).status_code == 403


def test_cadastro_rejeita_senha_muito_comum(cliente, emails):
    resposta = cliente.post('/usuarios', json={
        'usuario': 'nova', 'email': 'nova@example.com', 'senha': '12345678'})
    assert resposta.status_code == 422
    assert not emails


@pytest.mark.parametrize('usuario', ['   ', 'nome@example.com'])
def test_cadastro_recusa_usuario_inutilizavel(cliente, emails, usuario):
    resposta = cliente.post('/usuarios', json={
        'usuario': usuario, 'email': 'nova@example.com', 'senha': 'senha-segura'})
    assert resposta.status_code == 422


def test_login_por_email_longo(cliente):
    email = 'nome@' + 'a' * 60 + '.' + 'b' * 30 + '.com'
    with SessaoDeTeste() as sessao:
        conta = sessao.scalar(select(Usuario).where(Usuario.usuario == 'aline'))
        conta.email = email
        sessao.commit()
    resposta = cliente.post('/autenticacao/login', json={'usuario': email, 'senha': 'aline123'})
    assert resposta.status_code == 200


def test_configuracao_ausente_nao_persiste_cadastro(cliente, emails, monkeypatch):
    def indisponivel():
        raise RuntimeError('configuração ausente')
    monkeypatch.setattr(email_conta, 'validar_configuracao', indisponivel)
    assert cadastrar(cliente).status_code == 503
    with SessaoDeTeste() as sessao:
        assert sessao.scalar(select(Usuario).where(Usuario.usuario == 'nova')) is None


def test_falha_entrega_permite_novo_reenvio(cliente, emails, monkeypatch):
    def falhar(*args):
        raise OSError('SMTP indisponível')
    monkeypatch.setattr(email_conta, 'enviar', falhar)
    assert cadastrar(cliente).status_code == 201
    monkeypatch.setattr(email_conta, 'enviar', lambda *args: emails.append(args))
    assert cliente.post('/autenticacao/reenviar-confirmacao', json={'email': 'nova@example.com'}).status_code == 202
    assert cliente.post('/autenticacao/verificar-email', json={'token': token_email(emails)}).status_code == 200
