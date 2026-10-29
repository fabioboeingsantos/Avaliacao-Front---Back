# Frontend Cesta do Vale

Aplicação React/Vite da Cesta do Vale.

## Desenvolvimento local

```powershell
npm install
$env:VITE_URL_DA_API = "http://127.0.0.1:8000"
npm run dev
```

## Publicação na Vercel

Configure `frontend` como **Root Directory** de um projeto Vercel. O arquivo `vercel.json`
publica o build do Vite, mantém o fallback da SPA e encaminha `/api/*` para
`https://avaliacao-front-back-backend.vercel.app`.

Se a API receber outro domínio, altere o `destination` em `vercel.json` antes do deploy.
Na Vercel, configure a variável de build `VITE_URL_DA_API=/api`.
