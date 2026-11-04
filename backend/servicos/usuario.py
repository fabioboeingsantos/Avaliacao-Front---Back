"""Regras de cadastro e autenticação de usuários."""

from sqlalchemy.orm import Session

from modelos.usuario import Usuario
from repositorios import usuario as repositorio
from servicos.excecoes import UsuarioJaExiste
from seguranca import criar_hash_de_senha, senha_confere


def serializar_usuario(conta: Usuario) -> dict:
    """Retorna somente dados públicos da conta."""

    return {
        "id": conta.id,
        "usuario": conta.usuario,
        "email": conta.email,
        "perfil": conta.perfil,
        "grupo": conta.perfil,
        "ativo": conta.ativo,
        "email_verificado": conta.email_verificado,
    }


def cadastrar(sessao: Session, usuario: str, email: str, senha: str) -> dict:
    """Cria uma conta de assinante com senha protegida por Argon2."""

    usuario_normalizado = usuario.strip().lower()
    email_normalizado = email.strip().lower()
    if repositorio.buscar_por_usuario(sessao, usuario_normalizado):
        raise UsuarioJaExiste("Este usuário já está cadastrado.")
    if repositorio.buscar_por_email(sessao, email_normalizado):
        raise UsuarioJaExiste("Este e-mail já está cadastrado.")

    conta = Usuario(
        usuario=usuario_normalizado,
        email=email_normalizado,
        senha_hash=criar_hash_de_senha(senha),
        perfil="assinante",
        ativo=True,
    )
    from servicos import email_conta, tokens_conta
    sessao.add(conta)
    sessao.flush()
    mensagem = tokens_conta.emitir(sessao, conta, "confirmacao_email")
    sessao.commit()
    email_conta.enviar_com_seguranca(*mensagem)
    return serializar_usuario(conta)


def autenticar(sessao: Session, identificador: str, senha: str) -> dict | None:
    """Autentica por e-mail ou pelo usuário legado."""

    conta = (
        repositorio.buscar_por_email(sessao, identificador)
        if "@" in identificador
        else repositorio.buscar_por_usuario(sessao, identificador)
    )
    if conta is None or not conta.ativo or not senha_confere(senha, conta.senha_hash):
        return None

    return {
        "usuario": conta.usuario,
        "email": conta.email,
        "perfil": conta.perfil,
        "grupo": conta.perfil,
        "email_verificado": conta.email_verificado,
        "versao_sessao": conta.versao_sessao,
    }
