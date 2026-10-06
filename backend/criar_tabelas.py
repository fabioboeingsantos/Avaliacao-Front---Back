"""Cria as tabelas e carrega os dados mínimos para a demonstração."""

from banco import Base, Sessao, engine
from modelos.cesta import Produto
from modelos.usuarios import Usuario


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
    ("aline", "aline123", "assinante"),
    ("vanderlei", "vanderlei123", "produtor"),
]


def criar_tabelas() -> None:
    """Cria as tabelas sem apagar dados existentes e inclui dados ausentes."""

    Base.metadata.create_all(bind=engine)
    sessao = Sessao()
    try:
        for produto_id, nome in PRODUTOS_INICIAIS:
            if sessao.get(Produto, produto_id) is None:
                sessao.add(Produto(id=produto_id, nome=nome))

        for nome, senha, perfil in USUARIOS_INICIAIS:
            usuario_existente = sessao.query(Usuario).filter_by(usuario=nome).first()
            if usuario_existente is None:
                sessao.add(Usuario(usuario=nome, senha=senha, perfil=perfil))

        sessao.commit()
    finally:
        sessao.close()


if __name__ == "__main__":
    criar_tabelas()
    print("Tabelas e dados iniciais preparados.")
