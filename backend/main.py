"""Ponto de entrada da API FastAPI do Cesta do Vale."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configuracao import obter_origens_frontend
from rotas.autenticacao import router as rotas_de_autenticacao
from rotas.cestas import router as rotas_de_cestas
from rotas.sistemas import router as rotas_de_sistema
from rotas.usuarios import router as rotas_de_usuarios


app = FastAPI(
    title="Cesta do Vale API",
    description="API para pedidos e separação de cestas com persistência SQLAlchemy.",
    version="1.0.0",
)

# O CORS permite que o frontend Vite converse com a API em outra porta.
app.add_middleware(
    CORSMiddleware,
    allow_origins=obter_origens_frontend(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rotas_de_cestas)
app.include_router(rotas_de_autenticacao)
app.include_router(rotas_de_sistema)
app.include_router(rotas_de_usuarios)
