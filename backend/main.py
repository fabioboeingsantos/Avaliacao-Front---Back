"""Ponto de entrada da API FastAPI do Cesta do Vale."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configuracao import obter_origens_frontend
from rotas.cestas import router as rotas_de_cestas


app = FastAPI(
    title="Cesta do Vale API",
    description="API em memória para pedidos e separação de cestas semanais.",
    version="1.0.0",
)

# O CORS permite que o frontend Vite converse com a API em outra porta.
app.add_middleware(
    CORSMiddleware,
    allow_origins=obter_origens_frontend(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rotas_de_cestas)


@app.get("/saude", tags=["Sistema"])
def verificar_saude():
    """Confirma rapidamente que a API está ligada para os testes."""

    return {"status": "ok", "mensagem": "Cesta do Vale API online"}
