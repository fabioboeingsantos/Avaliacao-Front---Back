# Projeto da cartilha

Projeto estruturado para desenvolver o sistema da cartilha da aula 5.

## Como rodar o backend

O backend usa FastAPI em um ambiente virtual Python. Se o ambiente ainda não existir, na raiz do
projeto execute:

```powershell
uv python install 3.12
uv venv backend/.venv --python 3.12
uv pip install --python backend/.venv/Scripts/python.exe -r backend/requirements.txt
```

Depois, execute:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
fastapi dev main.py
```

Com a API ligada, o frontend envia os pedidos concluídos e as separações para o backend em memória.
O fluxo de demonstração é:

1. Entre como `aline` com a senha de teste `aline123`.
2. Crie e finalize uma cesta.
3. Saia pela opção de retorno e entre como `vanderlei` com a senha `vanderlei123`.
4. Abra a cesta na tela `A separação` e registre os produtos em `O fechamento`.

Rotas disponíveis:

- `GET /saude`: verifica se a API está online.
- `GET /cestas?assinante=aline&tamanho=pequena`: lista e filtra cestas.
- `GET /cestas/{id}`: mostra uma cesta.
- `POST /cestas`: cria uma cesta pedida.
- `GET /cestas/{id}/separacoes`: lista os produtos separados.
- `POST /cestas/{id}/separacoes`: registra uma separação e aplica o limite.

Depois, acesse `http://127.0.0.1:8000/docs` para visualizar a documentação da API.

## Como rodar o frontend

Na primeira vez, entre na pasta `frontend` e instale as dependências:

```powershell
cd frontend
npm install
```

Para iniciar o frontend:

```powershell
npm run dev
```

O Vite exibirá no terminal o endereço local da aplicação.

## Pastas

- `docs/`: cartilha, briefing, marca e styleguide.
- `frontend/`: aplicação React com o fluxo de pedido da assinante.
- `backend/`: API organizada em rotas, serviços, repositórios e esquemas.
