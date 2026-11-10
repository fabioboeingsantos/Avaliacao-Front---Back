# Frontend Cesta do Vale

Aplicação React/Vite da Cesta do Vale.

Guia revisado em 10/11/2026. Requer Node.js 22.12 ou superior e npm.
Veja também o [README principal](../README.md) e a [análise do sistema](../docs/ANALISE_SISTEMA.md).

## Desenvolvimento local

```powershell
cd frontend
npm install
$env:VITE_URL_DA_API = "http://127.0.0.1:8000"
npm run dev
```

Execute a entrada em `frontend` somente se o terminal ainda estiver na raiz do projeto.
O backend precisa estar ligado separadamente. No `.env` da raiz, defina
`FRONTEND_URL=http://localhost:5173,http://127.0.0.1:5173`.
Prefira abrir `http://127.0.0.1:5173` para usar o mesmo host da API.

O Vite carrega os arquivos de ambiente de `frontend/`. O arquivo versionado
`.env.development` aponta para a API local, enquanto `.env.production` usa `/api`.
Confira possíveis substituições em `.env.local` e reinicie o Vite após editar as variáveis.
Para celular na mesma rede, siga o roteiro de IP, CORS e portas no README principal.

## Verificação

Dentro de `frontend`:

```powershell
npm ci
npm run lint
npm run build
```

Lint e build passaram na revisão de 10/11/2026. Não há script de teste de navegador
no `package.json`; essas verificações não validam os fluxos com a API.

## Publicação na Vercel

Configure `frontend` como **Root Directory** de um projeto Vercel. O arquivo `vercel.json`
publica o build do Vite, mantém o fallback da SPA e encaminha `/api/*` para
`https://avaliacao-front-back-backend.vercel.app`.

Se a API receber outro domínio, altere o `destination` em `vercel.json` antes do deploy.
Na Vercel, configure a variável de build `VITE_URL_DA_API=/api`.

A URL é incorporada durante o build. Alterar a variável exige gerar e publicar um novo build.
