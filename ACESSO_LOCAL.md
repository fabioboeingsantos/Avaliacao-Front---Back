# Acesso ao servidor local

Este guia inicia a API e o frontend localmente pelo PowerShell. A configuração atual usa o banco PostgreSQL do Supabase, definido no `.env` da raiz. Estes passos são apenas para desenvolvimento e não fazem deploy.

Em 12/11/2026, o Python 3.12.10 foi restaurado, as dependências existentes da API carregaram corretamente, a API respondeu em `/health`, o frontend respondeu com HTTP 200 e a conexão com o Supabase foi confirmada com `SELECT 1`. Os serviços foram iniciados em segundo plano, conforme a seção abaixo.

No arquivo `.env` da raiz, use `FRONTEND_URL=http://localhost:5173,http://127.0.0.1:5173` para permitir o acesso do Vite à API. Os endereços da porta `8080` são para o Docker Compose.

## Preparação inicial

Execute os comandos a partir da raiz do projeto:

```powershell
cd C:\Users\fabio\Desktop\Avaliacao-Front---Back
```

### Python e dependências da API

Confira o Python pelo caminho usado nesta máquina, sem depender do launcher `py` ou do `PATH`:

```powershell
$pythonLocal = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
& $pythonLocal --version
```

Para instalar o Python 3.12:

```powershell
winget install --id Python.Python.3.12 --exact --scope user --accept-package-agreements --accept-source-agreements
```

Se o ambiente virtual mostrar `No Python at ...`, a instalação base pode estar ausente ou inacessível. Nesta máquina, `winget repair` não ofereceu reparo; a reinstalação abaixo restaurou o Python 3.12.10 e permitiu reutilizar o ambiente virtual existente:

```powershell
winget install --id Python.Python.3.12 --exact --scope user --force --accept-package-agreements --accept-source-agreements
& $pythonLocal --version
& .\backend\.venv\Scripts\python.exe --version
```

Se ocorrer `Acesso negado` em uma sessão restrita de automação, execute com a autorização de acesso necessária. Isso, por si só, não comprova que o Python está ausente.

Crie o ambiente e instale as dependências (uma vez, ou quando `requirements.txt` mudar):

```powershell
& $pythonLocal -m venv backend\.venv
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

## Configuração do banco e autenticação

A API carrega automaticamente o `.env` da raiz. `SUPABASE_DB_URL` tem prioridade sobre `DATABASE_URL` e sobre `BANCO_DRIVER`/`BANCO_NOME`. Assim, ter `BANCO_DRIVER=sqlite` no arquivo não ativa o SQLite enquanto uma URL externa estiver preenchida.

Mantenha a URL em `SUPABASE_DB_URL` e a senha em `SUPABASE_DB_PASSWORD`, sem copiá-las para a documentação. Para o banco remoto, preserve `sslmode=require` na URL. A chave `JWT_SECRET_KEY` também deve estar no `.env`, com pelo menos 32 caracteres. A inicialização abaixo usa essas configurações existentes.

Para optar pelo SQLite, deixe `SUPABASE_DB_URL` e `DATABASE_URL` vazias e configure `BANCO_DRIVER=sqlite` e `BANCO_NOME=./cesta_do_vale.db`. Com a API iniciada dentro de `backend`, esse arquivo fica em `backend/cesta_do_vale.db`.

## Iniciar a API em um terminal

Abra o primeiro terminal do PowerShell:

```powershell
cd C:\Users\fabio\Desktop\Avaliacao-Front---Back\backend
& .\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

O executável do ambiente virtual é chamado diretamente; não é necessário ativá-lo. Deixe o terminal da API aberto. Não é necessário executar `criar_tabelas.py` para iniciar a API usando o banco já configurado.

- API: `http://127.0.0.1:8000`
- Saúde da API: `http://127.0.0.1:8000/health`
- Documentação interativa: `http://127.0.0.1:8000/docs`

A rota `/` não tem uma página inicial e pode mostrar `{"detail":"Not Found"}`; isso não significa que a API esteja desligada.

## Iniciar o frontend

Abra um segundo terminal do PowerShell. O comando precisa ser executado dentro de `frontend`, onde está o `package.json`:

```powershell
cd C:\Users\fabio\Desktop\Avaliacao-Front---Back\frontend
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

Abra o endereço informado pelo Vite, normalmente `http://localhost:5173`. Se aparecer erro `ENOENT` procurando `package.json` na raiz, entre na pasta `frontend` e tente novamente.

## Iniciar em segundo plano

Este foi o modo usado na última inicialização. Execute na raiz do projeto, somente se as portas `8000` e `5173` estiverem livres:

```powershell
$projeto = (Get-Location).Path
New-Item -ItemType Directory -Path (Join-Path $projeto 'tmp') -Force | Out-Null
Start-Process -FilePath (Join-Path $projeto 'backend\.venv\Scripts\python.exe') -ArgumentList '-m','uvicorn','main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory (Join-Path $projeto 'backend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $projeto 'tmp\api-local.log') -RedirectStandardError (Join-Path $projeto 'tmp\api-local.err')
Start-Process -FilePath 'C:\Program Files\nodejs\node.exe' -ArgumentList 'node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','5173' -WorkingDirectory (Join-Path $projeto 'frontend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $projeto 'tmp\frontend-local.log') -RedirectStandardError (Join-Path $projeto 'tmp\frontend-local.err')
```

Após alguns segundos, confira os serviços:

```powershell
(Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/health').Content
(Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:5173').StatusCode
```

O resultado esperado é `status: ok` na API e `200` no frontend. A rota `/health` confirma que a API está ligada; ela não verifica o banco. Para confirmar a conexão sem alterar dados, execute dentro de `backend`:

```powershell
& .\.venv\Scripts\python.exe -c "from configuracao import obter_url_banco; from sqlalchemy import create_engine, text; engine = create_engine(obter_url_banco()); conn = engine.connect(); print(conn.execute(text('SELECT 1')).scalar()); conn.close(); engine.dispose()"
```

O resultado esperado é `1`. Se aparecer `password authentication failed`, atualize `SUPABASE_DB_PASSWORD` com a senha atual do projeto Supabase e reinicie a API. Consulte `tmp/api-local.err` e `tmp/frontend-local.err` se os serviços não iniciarem. Evite compartilhar logs que contenham credenciais.

## Contas de demonstração

- Assinante: usuário `aline`, senha `aline123`.
- Produtor: usuário `vanderlei`, senha `vanderlei123`.

Essas contas dependem dos dados cadastrados no banco selecionado. Sua existência no Supabase não foi verificada nesta inicialização.

## Encerrar

Se iniciou em dois terminais, pressione `Ctrl+C` em cada um. Se iniciou em segundo plano, identifique os processos nas portas usadas:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8000,5173 | Select-Object LocalAddress,LocalPort,OwningProcess
```

Confira o processo com `Get-Process -Id <OwningProcess>` e encerre somente o serviço desejado com `Stop-Process -Id <OwningProcess>`. Encerrar a API não apaga os dados do Supabase nem do SQLite.
