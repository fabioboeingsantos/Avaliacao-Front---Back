// Usa a URL definida pelo ambiente de desenvolvimento ou de produção do Vite.
const URL_DA_API = import.meta.env.VITE_URL_DA_API

if (!URL_DA_API) {
  throw new Error('Defina VITE_URL_DA_API no arquivo .env do ambiente do frontend.')
}

const CHAVE_TOKEN_SESSAO = 'cesta_do_vale_token_sessao'
function lerTokenSessao() {
  try {
    return typeof window !== 'undefined' ? window.sessionStorage?.getItem(CHAVE_TOKEN_SESSAO) || '' : ''
  } catch {
    return ''
  }
}

let tokenMemoria = lerTokenSessao()

function salvarTokenSessao(token) {
  tokenMemoria = token || ''
  try {
    if (tokenMemoria) window.sessionStorage?.setItem(CHAVE_TOKEN_SESSAO, tokenMemoria)
    else window.sessionStorage?.removeItem(CHAVE_TOKEN_SESSAO)
  } catch {}
}

// Centraliza as chamadas à API e mantém cookies de sessão em todas as requisições.
export async function chamarApi(caminho, opcoes = {}) {
  const cabecalhos = {
    'Content-Type': 'application/json',
    ...(tokenMemoria ? { Authorization: `Bearer ${tokenMemoria}` } : {}),
    ...(opcoes.headers ?? {}),
  }

  const resposta = await fetch(`${URL_DA_API.replace(/\/+$/, '')}${caminho}`, {
    ...opcoes,
    headers: cabecalhos,
    credentials: 'include',
  })

  if (!resposta.ok) {
    if (resposta.status === 401 && caminho === '/usuarios/me') {
      salvarTokenSessao('')
    }
    const corpo = await resposta.json().catch(() => ({}))
    const detalhe = Array.isArray(corpo.detail)
      ? corpo.detail.map((item) => `${item.loc?.at(-1) ?? 'Campo'}: ${item.msg}`).join('; ')
      : corpo.detail
    const erro = new Error(detalhe ?? 'Não foi possível concluir a operação.')
    erro.status = resposta.status
    throw erro
  }

  if (caminho === '/autenticacao/logout') {
    salvarTokenSessao('')
  }

  if (resposta.status === 204) {
    return null
  }

  const dados = await resposta.json()
  if (caminho === '/autenticacao/login' && dados?.access_token) {
    salvarTokenSessao(dados.access_token)
  }
  return dados
}
