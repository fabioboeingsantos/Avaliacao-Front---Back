"""Consulta e leitura das notificações persistentes da pessoa autenticada."""

from fastapi import APIRouter, Depends
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from banco import obter_sessao
from modelos.notificacao import Notificacao
from modelos.usuario import Usuario
from rotas.autenticacao import exigir_permissao

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])


@router.get("")
def listar_notificacoes(
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(exigir_permissao("notificacoes.listar")),
):
    registros = sessao.scalars(
        select(Notificacao)
        .where(Notificacao.usuario_id == usuario.id)
        .order_by(Notificacao.criada_em.desc(), Notificacao.id.desc())
        .limit(40)
    ).all()
    return [
        {
            "id": f"servidor-{item.id}",
            "cestaId": item.cesta_id,
            "titulo": item.titulo,
            "mensagem": item.mensagem,
            "criadaEm": item.criada_em.isoformat(),
            "lida": item.lida,
        }
        for item in registros
    ]


@router.post("/lidas", status_code=204)
def marcar_notificacoes_lidas(
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(exigir_permissao("notificacoes.marcar_lidas")),
):
    sessao.execute(
        update(Notificacao)
        .where(Notificacao.usuario_id == usuario.id, Notificacao.lida.is_(False))
        .values(lida=True)
    )
    sessao.commit()
