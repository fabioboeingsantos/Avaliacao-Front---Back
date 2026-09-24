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
- `frontend/`: aplicação React e suas quatro telas.
- `backend/`: API organizada em rotas, serviços, repositórios e esquemas.
