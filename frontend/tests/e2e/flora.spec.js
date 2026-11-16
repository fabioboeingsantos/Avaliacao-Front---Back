import { test, expect } from '@playwright/test'

const produto = { id: 'alface', nome: 'Alface', preco_unitario: 1.5, estoque: 10, categoria: 'Verduras' }
const proposta = { status: 'proposta', mensagem: 'Revise a sugestão antes de confirmar.', qa: { status: 'aprovado' }, proposta: { tipo: 'pedido_cesta', tamanho: 'pequena', modo: 'selecionavel', produtos: [{ produto_id: 'alface', quantidade: 2 }] } }

test.beforeEach(async ({ page }) => {
  await page.route('**/api/**', async (route) => {
    const path = new URL(route.request().url()).pathname
    let json = []
    if (path.endsWith('/usuarios/me')) json = { usuario: 'aline', perfil: 'assinante' }
    if (path.endsWith('/produtos')) json = [produto]
    if (path.endsWith('/assistente/analisar') || path.endsWith('/assistente/pedido')) {
      const mensagem = route.request().postDataJSON().mensagem
      json = /catálogo/i.test(mensagem)
        ? { status: 'consulta', visualizacao: { tipo: 'catalogo', resumo: 'Escolha os produtos.', produtos: [produto], maximo_unidades: 5 } }
        : proposta
    }
    if (path.endsWith('/cestas') && route.request().method() === 'POST') json = { id: 100 }
    await route.fulfill({ json })
  })
  await page.goto('/flora')
  await expect(page.getByRole('heading', { name: 'Flora', exact: true })).toBeVisible()
})

async function pedirCesta(page) {
  await page.getByRole('button', { name: /^Montar cesta Escolha seus/ }).click()
  await page.getByRole('button', { name: /Cesta selecionável/ }).click()
  await page.getByLabel('Sua mensagem', { exact: true }).fill('Quero 2 alfaces')
  const propostaRecebida = page.waitForResponse((resposta) =>
    new URL(resposta.url()).pathname === '/api/assistente/pedido' &&
    resposta.request().method() === 'POST',
  )
  await page.getByRole('button', { name: 'Enviar', exact: true }).click()
  expect((await propostaRecebida).ok()).toBe(true)
  await expect(page.getByRole('button', { name: 'Confirmar cesta', exact: true })).toBeVisible()
}

test('ajusta a prévia pelo chat e desfaz antes de confirmar', async ({ page }) => {
  await page.route('**/api/assistente/pedido', async (route) => {
    const { mensagem, rascunho } = route.request().postDataJSON()
    if (mensagem === 'Só uma alface') {
      expect(rascunho).toEqual(proposta.proposta)
      await route.fulfill({ json: {
        ...proposta,
        proposta: { ...proposta.proposta, produtos: [{ produto_id: 'alface', quantidade: 1 }] },
      } })
    } else {
      await route.fulfill({ json: proposta })
    }
  })
  await pedirCesta(page)
  const previa = page.getByRole('region', { name: 'Cesta pequena' })
  await expect(previa).toContainText(/R\$\s*3,00/)
  await page.getByRole('button', { name: 'Ajustar itens' }).click()
  await expect(page.getByLabel('Sua mensagem', { exact: true })).toBeFocused()
  await page.getByLabel('Sua mensagem', { exact: true }).fill('Só uma alface')
  await page.getByRole('button', { name: 'Enviar', exact: true }).click()
  await expect(previa).toContainText('Quantidade ajustada')
  await expect(previa).toContainText(/R\$\s*1,50/)
  await page.getByRole('button', { name: 'Desfazer último ajuste' }).click()
  await expect(previa).toContainText('2 × Alface')
  await expect(previa).toContainText(/R\$\s*3,00/)
})

test('confirma uma vez e substitui a resposta por agradecimento', async ({ page }) => {
  let pedidos = 0
  page.on('request', (req) => { if (req.method() === 'POST' && new URL(req.url()).pathname === '/api/cestas') pedidos += 1 })
  await pedirCesta(page)
  expect(pedidos).toBe(0)
  await page.getByRole('button', { name: 'Confirmar cesta', exact: true }).click()
  await expect(page.getByText('Muito obrigada por escolher a Cesta do Vale', { exact: false })).toBeVisible()
  await expect(page.getByText('Revise a sugestão antes de confirmar.', { exact: true })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Confirmar cesta', exact: true })).toHaveCount(0)
  expect(pedidos).toBe(1)
  await expect(page.locator('header.flora-cabecalho').getByText('Pedido confirmado com sucesso.')).toHaveCount(1)
  await expect(page.getByText('Proposta pronta e conferida · Aguardando confirmação')).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Continuar nos meus pedidos' })).toBeVisible()
})

test('cancelamento encerra a proposta sem enviar pedido', async ({ page }) => {
  let pedidos = 0
  page.on('request', (req) => { if (req.method() === 'POST' && new URL(req.url()).pathname === '/api/cestas') pedidos += 1 })
  await pedirCesta(page)
  await page.getByRole('button', { name: 'Cancelar', exact: true }).click()
  await expect(page.getByText('Cesta cancelada.', { exact: false })).toBeVisible()
  expect(pedidos).toBe(0)
})

test('catálogo soma, subtrai e retira itens sem ultrapassar limite', async ({ page }) => {
  await page.getByRole('button', { name: /Ver catálogo/ }).click()
  const adicionar = page.getByRole('button', { name: 'Adicionar uma unidade de Alface' })
  await adicionar.click({ clickCount: 2 })
  await expect(page.getByLabel('2 unidades de Alface')).toBeVisible()
  await page.getByRole('button', { name: 'Retirar uma unidade de Alface' }).click()
  await expect(page.getByLabel('1 unidades de Alface')).toBeVisible()
  await page.getByRole('button', { name: 'Retirar item' }).click()
  await expect(page.getByLabel('0 unidades de Alface')).toBeVisible()
  for (let i = 0; i < 5; i += 1) await adicionar.click()
  await expect(adicionar).toBeDisabled()
  const semRolagemHorizontal = await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)
  expect(semRolagemHorizontal).toBe(true)
})

test('consulta o catálogo durante a montagem e envia os produtos escolhidos', async ({ page }) => {
  await page.route('**/api/assistente/pedido', async (route) => {
    expect(route.request().postDataJSON().mensagem).toContain('2 Alface')
    await route.fulfill({ json: proposta })
  })
  await page.getByRole('button', { name: /^Montar cesta Escolha seus/ }).click()
  await page.getByRole('button', { name: /Cesta selecionável/ }).click()
  const consulta = page.waitForResponse((resposta) =>
    new URL(resposta.url()).pathname === '/api/assistente/analisar' &&
    resposta.request().postDataJSON().mensagem === 'Mostre o catálogo completo.',
  )
  await page.getByRole('button', { name: 'Consultar catálogo' }).click()
  expect((await consulta).ok()).toBe(true)
  const adicionar = page.getByRole('button', { name: 'Adicionar uma unidade de Alface' })
  await adicionar.click({ clickCount: 2 })
  await expect(page.getByLabel('Sua mensagem', { exact: true })).toHaveValue(/2 Alface/)
  await page.getByRole('button', { name: 'Enviar', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Confirmar cesta', exact: true })).toBeVisible()
})
