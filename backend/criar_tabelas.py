"""Cria as tabelas e carrega os dados mínimos para a demonstração."""

from sqlalchemy import inspect, text

from banco import Base, Sessao, engine
from modelos.cesta import Cesta
from modelos.produto import Produto
from modelos.usuario import Usuario
from seguranca import criar_hash_de_senha, senha_ja_esta_protegida


PRODUTOS_INICIAIS = [
    ("alface", "Alface", 150),
    ("tomate", "Tomate", 250),
    ("cenoura", "Cenoura", 150),
    ("batata", "Batata", 200),
    ("cebola", "Cebola", 125),
    ("couve", "Couve", 150),
    ("beterraba", "Beterraba", 150),
    ("abobrinha", "Abobrinha", 200),
    ("chuchu", "Chuchu", 125),
    ("pimentao", "Pimentão", 250),
    ("pepino", "Pepino", 150),
    ("mandioca", "Mandioca", 200),
]

USUARIOS_INICIAIS = [
    ("aline", "aline@cestadovale.com", "aline123", "assinante"),
    ("vanderlei", "vanderlei@cestadovale.com", "vanderlei123", "produtor"),
]


def criar_tabelas() -> None:
    """Cria as tabelas sem apagar dados existentes e inclui dados ausentes."""

    Base.metadata.create_all(bind=engine)
    # Mantém bancos locais antigos compatíveis com as colunas adicionadas ao catálogo.
    colunas_produtos = {coluna["name"] for coluna in inspect(engine).get_columns("produtos")}
    preco_adicionado_agora = "preco_centavos" not in colunas_produtos
    if "estoque" not in colunas_produtos or "preco_centavos" not in colunas_produtos:
        # create_all não altera tabelas existentes; atualiza o banco local sem apagar dados.
        with engine.begin() as conexao:
            if "estoque" not in colunas_produtos:
                conexao.execute(text("ALTER TABLE produtos ADD COLUMN estoque INTEGER NOT NULL DEFAULT 20"))
            if preco_adicionado_agora:
                conexao.execute(text("ALTER TABLE produtos ADD COLUMN preco_centavos INTEGER NOT NULL DEFAULT 500"))

    # Bancos que já tinham pedidos também recebem o preço congelado de cada item.
    colunas_itens = {coluna["name"] for coluna in inspect(engine).get_columns("itens_cesta")}
    if "preco_unitario_centavos" not in colunas_itens:
        with engine.begin() as conexao:
            conexao.execute(text("ALTER TABLE itens_cesta ADD COLUMN preco_unitario_centavos INTEGER"))
            conexao.execute(
                text(
                    "UPDATE itens_cesta SET preco_unitario_centavos = "
                    "(SELECT preco_centavos FROM produtos WHERE produtos.id = itens_cesta.produto_id)"
                )
            )

    # Bancos locais antigos recebem as colunas de avaliação sem perder pedidos existentes.
    colunas_cestas = {coluna["name"] for coluna in inspect(engine).get_columns("cestas")}
    colunas_avaliacao = {
        "avaliacao_assinante": "avaliacao_assinante",
        "avaliacao_produtor": "avaliacao_produtor",
    }
    colunas_faltantes = [
        nome_coluna for nome_coluna in colunas_avaliacao if nome_coluna not in colunas_cestas
    ]
    if colunas_faltantes:
        with engine.begin() as conexao:
            for nome_coluna in colunas_faltantes:
                conexao.execute(text(f"ALTER TABLE cestas ADD COLUMN {nome_coluna} INTEGER"))

    sessao = Sessao()
    try:
        for produto_id, nome, preco_centavos in PRODUTOS_INICIAIS:
            if sessao.get(Produto, produto_id) is None:
                sessao.add(Produto(id=produto_id, nome=nome, preco_centavos=preco_centavos))
            elif preco_adicionado_agora:
                # Atualiza bancos antigos com os preços definidos para o catálogo.
                sessao.get(Produto, produto_id).preco_centavos = preco_centavos

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
