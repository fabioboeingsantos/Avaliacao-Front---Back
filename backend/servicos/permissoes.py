"""Grupos de usuários e permissões do sistema."""

# Cada persona do projeto possui um grupo fixo de acesso.
# Esses valores também são armazenados no campo `perfil` da tabela de usuários.
GRUPO_ASSINANTE = "assinante"
GRUPO_PRODUTOR = "produtor"


# A matriz centraliza as permissões para que as rotas não precisem repetir
# verificações diferentes ou criar regras de acesso espalhadas pelo sistema.
PERMISSOES_POR_GRUPO = {
    GRUPO_ASSINANTE: {
        "usuarios.consultar_propria_conta",
        "cestas.listar",
        "cestas.consultar",
        "cestas.listar_separacoes",
        "cestas.criar",
    },
    GRUPO_PRODUTOR: {
        "usuarios.consultar_propria_conta",
        "cestas.listar",
        "cestas.consultar",
        "cestas.listar_separacoes",
        "cestas.registrar_separacao",
    },
}


def grupo_tem_permissao(grupo: str, permissao: str) -> bool:
    """Informa se o grupo possui a permissão solicitada."""

    # Grupos desconhecidos não recebem acesso por padrão.
    return permissao in PERMISSOES_POR_GRUPO.get(grupo, set())
