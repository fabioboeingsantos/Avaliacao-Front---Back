// Usa a URL definida pelo ambiente de desenvolvimento ou de produção do Vite.
const URL_DA_API = import.meta.env.VITE_URL_DA_API

if (!URL_DA_API) {
  throw new Error('Defina VITE_URL_DA_API no arquivo .env do ambiente do frontend.')
}

// Centraliza as chamadas à API e mantém cookies de sessão em todas as requisições.
export async function chamarApi(caminho, opcoes = {}) {
  const cabecalhos = {
    'Content-Type': 'application/json',
    ...(opcoes.headers ?? {}),
  }

  const resposta = await fetch(`${URL_DA_API.replace(/\/+$/, '')}${caminho}`, {
    ...opcoes,
    headers: cabecalhos,
    credentials: 'include',
  })

  if (!resposta.ok) {
    const corpo = await resposta.json().catch(() => ({}))
    const erro = new Error(corpo.detail ?? 'Não foi possível concluir a operação.')
    erro.status = resposta.status
    throw erro
  }

  if (resposta.status === 204) {
    return null
  }

  return resposta.json()
}
