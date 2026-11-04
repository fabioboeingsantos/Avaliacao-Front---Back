"""Valida TLS/SSL, sanitização dos logs e migração de contas antigas."""

import importlib.util
from pathlib import Path
import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text
from servicos import email_conta


@pytest.mark.parametrize('seguranca', ['starttls', 'ssl'])
def test_smtp_envia_com_tls_e_autenticacao(monkeypatch, seguranca):
    for nome, valor in {'EMAIL_FRONTEND_URL': 'https://cesta.example.com',
                        'SMTP_HOST': 'smtp.example.com', 'SMTP_FROM': 'contas@example.com',
                        'SMTP_USER': 'usuario', 'SMTP_PASSWORD': 'senha-do-provedor',
                        'SMTP_SECURITY': seguranca, 'SMTP_PORT': '587' if seguranca == 'starttls' else '465'}.items():
        monkeypatch.setenv(nome, valor)
    eventos = []

    class SMTP:
        def __init__(self, host, porta, **kwargs):
            eventos.append(('conectar', host, porta, kwargs))
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def starttls(self, **kwargs):
            eventos.append(('tls', kwargs))
        def login(self, usuario, senha):
            eventos.append(('login', usuario, senha))
        def send_message(self, mensagem):
            eventos.append(('enviar', mensagem))

    monkeypatch.setattr(email_conta.smtplib, 'SMTP' if seguranca == 'starttls' else 'SMTP_SSL', SMTP)
    email_conta.enviar('destino@example.com', 'Confirme sua conta', 'link de teste')
    assert eventos[-1][0] == 'enviar'
    assert eventos[-1][1]['To'] == 'destino@example.com'
    assert eventos[-1][1]['From'] == 'contas@example.com'
    assert eventos[-2] == ('login', 'usuario', 'senha-do-provedor')
    if seguranca == 'starttls':
        assert eventos[1][0] == 'tls'
        assert eventos[1][1]['context'].check_hostname
    else:
        assert eventos[0][3]['context'].check_hostname


@pytest.mark.parametrize('origem', ['http://cesta.example.com', 'https://usuario:senha@cesta.example.com',
                                  'https://cesta.example.com/?token=segredo', ''])
def test_configuracao_recusa_origem_insegura(monkeypatch, origem):
    monkeypatch.setenv('EMAIL_FRONTEND_URL', origem)
    monkeypatch.setenv('SMTP_HOST', 'smtp.example.com')
    monkeypatch.setenv('SMTP_FROM', 'contas@example.com')
    with pytest.raises(RuntimeError):
        email_conta.validar_configuracao()


def test_falha_smtp_nao_expoe_conteudo(caplog, monkeypatch):
    def falhar(*args):
        raise OSError('token-super-secreto email@example.com senha-do-provedor')
    monkeypatch.setattr(email_conta, 'enviar', falhar)
    email_conta.enviar_com_seguranca('email@example.com', 'assunto', 'token-super-secreto')
    assert 'Falha na entrega' in caplog.text
    assert 'token-super-secreto' not in caplog.text
    assert 'email@example.com' not in caplog.text
    assert 'senha-do-provedor' not in caplog.text


def test_migracao_preserva_contas_e_exige_confirmacao():
    arquivo = Path(__file__).parents[1] / 'migracoes/versions/20261104_0012_tokens_conta.py'
    spec = importlib.util.spec_from_file_location('migracao_tokens', arquivo)
    migracao = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migracao)
    engine = create_engine('sqlite://')
    with engine.begin() as conexao:
        conexao.execute(text('CREATE TABLE usuarios (id INTEGER PRIMARY KEY, usuario TEXT NOT NULL)'))
        conexao.execute(text("INSERT INTO usuarios VALUES (1, 'existente')"))
        with Operations.context(MigrationContext.configure(conexao)):
            migracao.upgrade()
        conta = conexao.execute(text('SELECT * FROM usuarios')).mappings().one()
        assert conta['usuario'] == 'existente'
        assert conta['email_verificado'] == 0
        assert conta['versao_sessao'] == 0
        assert 'tokens_conta' in inspect(conexao).get_table_names()
        with Operations.context(MigrationContext.configure(conexao)):
            migracao.downgrade()
        assert conexao.execute(text('SELECT usuario FROM usuarios')).scalar_one() == 'existente'
    engine.dispose()
