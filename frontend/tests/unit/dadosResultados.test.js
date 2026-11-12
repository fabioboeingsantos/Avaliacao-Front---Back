import { test } from 'node:test'
import assert from 'node:assert/strict'
import { moeda, nomeTamanho, dataSemana, itensDaProposta, textoDoResultado } from '../../src/funcionalidades/assistente/dadosResultados.js'

test('formata tamanhos, moeda e datas inválidas', () => {
  assert.equal(nomeTamanho('media'), 'média')
  assert.match(moeda(12.5), /12,50/)
  assert.equal(dataSemana('inválida'), null)
  assert.equal(dataSemana('2026-11-12'), '12/11/2026')
})

test('calcula centavos e mantém itens antigos sem produto cadastrado', () => {
  const itens = itensDaProposta({ produtos: [{ produto_id: 'alface', quantidade: 2 }, { produto_id: 'antigo', quantidade: 1 }] }, [{ id: 'alface', nome: 'Alface', precoUnitario: 1.5 }])
  assert.equal(itens[0].centavos, 150)
  assert.equal(itens[1].nome, 'antigo')
  assert.equal(itens[1].centavos, null)
})

test('texto da resposta inclui itens e quantidades para áudio', () => {
  const texto = textoDoResultado({ mensagem: 'Revise.', proposta: { tamanho: 'pequena', produtos: [{ produto_id: 'alface', quantidade: 2 }] } }, [{ id: 'alface', nome: 'Alface' }])
  assert.match(texto, /2 unidades de Alface/)
  assert.match(texto, /Cesta pequena/)
})
