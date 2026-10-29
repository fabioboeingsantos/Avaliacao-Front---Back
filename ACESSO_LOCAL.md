# Acesso ao servidor local

Este guia inicia a API e o frontend em dois terminais do PowerShell. O banco local usa SQLite. Estes passos são apenas para desenvolvimento e não fazem deploy.

No arquivo `.env` da raiz, use `FRONTEND_URL=http://localhost:5173,http://127.0.0.1:5173` para permitir o acesso do Vite à API. Os endereços da porta `8080` são para o Docker Compose.

## Preparação inicial

Execute os comandos a partir da raiz do projeto:

```powershell
cd C:\Users\fabio\Desktop\Avaliacao-Front---Back
```

### Python e dependências da API

Confira se o Python 3.12 está instalado:

```powershell
py -3.12 --version
```

Se o launcher disser que não há runtime instalado, instale-o uma vez:

```powershell
py install 3.12
```

Crie o ambiente e instale as dependências (uma vez, ou quando `requirements.txt` mudar):

```powershell
py -3.12 -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install --upgrade pip
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

### Node e dependências do frontend

Configure o endereço local da API em `frontend/.env.local` (uma vez):

```env
VITE_URL_DA_API=http://127.0.0.1:8000
```

Instale as dependências do frontend uma vez, dentro da pasta `frontend`:

```powershell
cd C:\Users\fabio\Desktop\Avaliacao-Front---Back\frontend
npm install
```

## Iniciar a API

Abra o primeiro terminal do PowerShell:

```powershell
cd C:\Users\fabio\Desktop\Avaliacao-Front---Back\backend
.\.venv\Scripts\Activate.ps1
$env:JWT_SECRET_KEY = "chave-local-de-desenvolvimento-com-mais-de-32-caracteres"
python criar_tabelas.py
python -m fastapi dev main.py
```

Confirme que o prompt mostra `(.venv)`. Se a ativação falhar, pare e confira se a etapa de preparação criou `backend\.venv`. Deixe o terminal da API aberto.

- API: `http://127.0.0.1:8000`
- Saúde da API: `http://127.0.0.1:8000/saude`
- Documentação interativa: `http://127.0.0.1:8000/docs`

A rota `/` não tem uma página inicial e pode mostrar `{"detail":"Not Found"}`; isso não significa que a API esteja desligada.

## Iniciar o frontend

Abra um segundo terminal do PowerShell. O comando precisa ser executado dentro de `frontend`, onde está o `package.json`:

```powershell
cd C:\Users\fabio\Desktop\Avaliacao-Front---Back\frontend
npm run dev
```

Abra o endereço informado pelo Vite, normalmente `http://localhost:5173`. Se aparecer erro `ENOENT` procurando `package.json` na raiz, entre na pasta `frontend` e tente novamente.

## Contas de demonstração

- Assinante: usuário `aline`, senha `aline123`.
- Produtor: usuário `vanderlei`, senha `vanderlei123`.

## Encerrar

Pressione `Ctrl+C` em cada terminal. A chave JWT definida com `$env:` vale somente para o terminal atual. Os dados do SQLite permanecem no arquivo local do banco.
