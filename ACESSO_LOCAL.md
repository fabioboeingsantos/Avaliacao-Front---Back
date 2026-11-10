# Acesso local rápido

Este é o roteiro principal para iniciar o projeto localmente. Ele foi pensado para que a leitura deste arquivo seja suficiente para testar a aplicação sem nova investigação.

## Início rápido

Abra um PowerShell na raiz do projeto:

```powershell
$raiz = 'C:\Users\fabio\Desktop\Avaliacao Front - Back'
Set-Location $raiz
```

### 1. Inicie a API

O ambiente `.supabase-venv` já contém as dependências completas usadas pela API neste computador:

```powershell
$python = Join-Path $raiz '.supabase-venv\Scripts\python.exe'
Start-Process -FilePath $python `
  -ArgumentList '-m','uvicorn','main:app','--host','127.0.0.1','--port','8000' `
  -WorkingDirectory (Join-Path $raiz 'backend') `
  -WindowStyle Hidden
```

### 2. Inicie o frontend

```powershell
Start-Process -FilePath 'npm.cmd' `
  -ArgumentList 'run','dev','--','--host','127.0.0.1' `
  -WorkingDirectory (Join-Path $raiz 'frontend')
```

Abra:

- Aplicação: <http://localhost:5173>
- API: <http://127.0.0.1:8000>
- Documentação da API: <http://127.0.0.1:8000/docs>

## Verificação rápida

A rota `/health` confirma somente que a API está ligada. Para verificar o banco de verdade, execute:

```powershell
Set-Location (Join-Path $raiz 'backend')
& (Join-Path $raiz '.supabase-venv\Scripts\python.exe') -c "from banco import engine; from sqlalchemy import text; c=engine.connect(); print(c.execute(text('SELECT 1')).scalar()); c.close()"
```

O resultado esperado é `1`. Se aparecer `password authentication failed`, a API está ligada, mas a senha do Supabase no `.env` está incorreta ou desatualizada. Atualize `SUPABASE_DB_PASSWORD` com a senha atual do projeto Supabase e reinicie a API antes de tentar acessar contas.

## Banco usado pelo ambiente

O arquivo `.env` fica na raiz do projeto. A regra atual é:

1. Se `BANCO_DRIVER=sqlite` estiver definido, a API usa SQLite local, mesmo que variáveis do Supabase existam.
2. Se `SUPABASE_DB_URL` existir e `BANCO_DRIVER` for diferente de `sqlite` (por exemplo, `postgresql`), a API usa Supabase/PostgreSQL.
3. Para desenvolvimento sem banco remoto, mantenha esta configuração. Neste computador, `BANCO_DRIVER=postgresql` seleciona o Supabase; o acesso às contas depende de `SUPABASE_DB_PASSWORD` estar atualizada:

```env
SUPABASE_DB_URL=
SUPABASE_DB_PASSWORD=
BANCO_DRIVER=sqlite
BANCO_NOME=./cesta_do_vale.db
```

Depois de alterar o `.env`, reinicie a API. Não publique a senha do Supabase nem a inclua em commits.

## Configuração inicial

Se o ambiente Python ainda não existir, crie-o e instale as dependências:

```powershell
py -3.12 -m venv .supabase-venv
.supabase-venv\Scripts\python.exe -m pip install -r requirements.txt
```

Para o frontend:

```powershell
Set-Location (Join-Path $raiz 'frontend')
npm.cmd install
```

Se necessário, crie `frontend/.env.local` com:

```env
VITE_URL_DA_API=http://127.0.0.1:8000
```

## Contas de demonstração

As contas abaixo só existem nos bancos que foram preparados com esses dados. Elas não são criadas automaticamente ao iniciar a API; confirme que estão cadastradas no Supabase antes de tentar entrar.

- Assinante: usuário `aline`, senha `aline123`.
- Produtor: usuário `vanderlei`, senha `vanderlei123`.

## Parar os servidores

Para fechar os processos iniciados em segundo plano:

```powershell
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
  Where-Object { $_.LocalPort -in 5173,8000 } |
  Select-Object -ExpandProperty OwningProcess -Unique |
  Stop-Process -Force
```

Se preferir acompanhar os logs, inicie `uvicorn` e `npm.cmd run dev` diretamente em dois terminais e encerre cada um com `Ctrl+C`.
