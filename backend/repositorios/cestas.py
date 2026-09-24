# Esta lista representa o armazenamento temporário das cestas.
# Ela fica no repositório porque o projeto ainda não utiliza banco de dados.
cestas = []

# Este catálogo concentra os produtos que podem aparecer nas composições.
# O serviço poderá consultar estes dados sem depender de uma lista no frontend.
produtos_disponiveis = [
    {"id": "alface", "nome": "Alface"},
    {"id": "tomate", "nome": "Tomate"},
    {"id": "cenoura", "nome": "Cenoura"},
    {"id": "batata", "nome": "Batata"},
    {"id": "cebola", "nome": "Cebola"},
    {"id": "couve", "nome": "Couve"},
    {"id": "beterraba", "nome": "Beterraba"},
    {"id": "abobrinha", "nome": "Abobrinha"},
    {"id": "chuchu", "nome": "Chuchu"},
    {"id": "pimentao", "nome": "Pimentão"},
    {"id": "pepino", "nome": "Pepino"},
    {"id": "mandioca", "nome": "Mandioca"},
]

# Esta estrutura registra os produtos de cada cesta pronta.
# Ela descreve o conteúdo cadastrado, mas não decide se uma cesta pode ser criada.
composicoes_prontas = {
    "pequena": ["alface", "tomate", "cenoura", "batata", "cebola"],
    "media": [
        "alface",
        "tomate",
        "cenoura",
        "batata",
        "cebola",
        "couve",
        "beterraba",
        "abobrinha",
    ],
    "grande": [
        "alface",
        "tomate",
        "cenoura",
        "batata",
        "cebola",
        "couve",
        "beterraba",
        "abobrinha",
        "chuchu",
        "pimentao",
        "pepino",
        "mandioca",
    ],
}


# A função centraliza a leitura das cestas para que a rota não acesse
# diretamente a lista mantida pelo repositório.
def listar_cestas():
    return cestas


# A busca por identificador fica no repositório porque ela apenas localiza
# um dado armazenado e não decide se a operação é permitida.
def buscar_cesta_por_id(id_cesta: int):
    for cesta in cestas:
        if cesta["id"] == id_cesta:
            return cesta

    return None


# A inclusão de uma cesta fica separada da regra de criação para que o serviço
# possa validar os dados antes de gravá-los na lista em memória.
def adicionar_cesta(cesta: dict):
    cestas.append(cesta)
    return cesta


# A atualização substitui a cesta encontrada sem aplicar regra de negócio.
# A decisão sobre o que pode ser alterado pertence ao serviço.
def atualizar_cesta(cesta_atualizada: dict):
    for indice, cesta in enumerate(cestas):
        if cesta["id"] == cesta_atualizada["id"]:
            cestas[indice] = cesta_atualizada
            return cesta_atualizada

    return None


# A função disponibiliza o catálogo para o serviço, mantendo os produtos
# cadastrados fora das rotas e dos componentes React.
def listar_produtos_disponiveis():
    return produtos_disponiveis


# A função transforma a composição cadastrada em produtos com quantidade.
# A quantidade inicial igual a 1 é um dado da cesta pronta desta proposta;
# a validação do limite continua sendo responsabilidade do serviço.
def buscar_composicao_pronta(tamanho: str):
    ids_dos_produtos = composicoes_prontas.get(tamanho)

    if ids_dos_produtos is None:
        return None

    produtos_da_cesta = []

    for id_produto in ids_dos_produtos:
        for produto in produtos_disponiveis:
            if produto["id"] == id_produto:
                produtos_da_cesta.append(
                    {
                        "nome": produto["nome"],
                        "quantidade": 1,
                    }
                )
                break

    return produtos_da_cesta
