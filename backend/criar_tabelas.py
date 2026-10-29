"""Cria as tabelas e carrega os dados mínimos para a demonstração."""

from sqlalchemy import inspect, text

from banco import Base, Sessao, engine
from modelos.cesta import Cesta
from modelos.produto import Produto
from modelos.usuario import Usuario
from seguranca import criar_hash_de_senha, senha_ja_esta_protegida


PRODUTOS_INICIAIS = [
    ("alface", "Alface"),
    ("tomate", "Tomate"),
    ("cenoura", "Cenoura"),
    ("batata", "Batata"),
    ("cebola", "Cebola"),
    ("couve", "Couve"),
    ("beterraba", "Beterraba"),
    ("abobrinha", "Abobrinha"),
    ("chuchu", "Chuchu"),
    ("pimentao", "Pimentão"),
    ("pepino", "Pepino"),
    ("mandioca", "Mandioca"),
]

USUARIOS_INICIAIS = [
    ("aline", "aline@cestadovale.com", "aline123", "assinante"),
    ("vanderlei", "vanderlei@cestadovale.com", "vanderlei123", "produtor"),
]


def criar_tabelas() -> None:
    """Cria as tabelas sem apagar dados existentes e inclui dados ausentes."""

    Base.metadata.create_all(bind=engine)
    colunas_produtos = {coluna["name"] for coluna in inspect(engine).get_columns("produtos")}
    if "estoque" not in colunas_produtos:
        # create_all não altera tabelas existentes; atualiza o banco local sem apagar dados.
        with engine.begin() as conexao:
            conexao.execute(
                text("ALTER TABLE produtos ADD COLUMN estoque INTEGER NOT NULL DEFAULT 20")
            )
    sessao = Sessao()
    try:
        for produto_id, nome in PRODUTOS_INICIAIS:
            if sessao.get(Produto, produto_id) is None:
                sessao.add(Produto(id=produto_id, nome=nome))

        for nome, email, senha, perfil in USUARIOS_INICIAIS:
            usuario_existente = sessao.query(Usuario).filter_by(usuario=nome).first()
            if usuario_existente is None:
                # Novas contas entram no banco somente depois de receber o hash Argon2.
                sessao.add(
                    Usuario(
                        usuario=nome,
                        email=email,
                        senha_hash=criar_hash_de_senha(senha),
                        perfil=perfil,
                    )
                )
            else:
                if not usuario_existente.email:
                    usuario_existente.email = email
                if not senha_ja_esta_protegida(usuario_existente.senha_hash):
                    # Atualiza contas antigas que foram criadas antes da protecao das senhas.
                    usuario_existente.senha_hash = criar_hash_de_senha(usuario_existente.senha_hash)

        # Vincula registros antigos pelo assinante para nao perder seu historico.
        usuarios = {usuario.usuario: usuario.id for usuario in sessao.query(Usuario).all()}
        for cesta in sessao.query(Cesta).filter(Cesta.usuario_id.is_(None)).all():
            if cesta.assinante in usuarios:
                cesta.usuario_id = usuarios[cesta.assinante]

        sessao.commit()
    finally:
        sessao.close()


if __name__ == "__main__":
    criar_tabelas()
    print("Tabelas e dados iniciais preparados.")
