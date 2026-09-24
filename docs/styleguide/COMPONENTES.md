# Styleguide de componentes — Cesta do Vale

> Componentes base para as quatro telas: duas da Aline e duas do Vanderlei. Eles definem aparência
> e comportamento visual; não acrescentam funcionalidades além da cartilha e do briefing.

## 1. Princípios

- Um componente deve ter texto claro e uma ação principal evidente.
- A interface deve funcionar primeiro no celular e continuar confortável no computador.
- Estados de carregamento, erro, sucesso e desabilitado devem ser visíveis.
- Cor nunca será o único indicador de situação.
- O foco do teclado deve permanecer visível.

## 2. Botões

### Primário

Usado para a ação principal da tela, como confirmar um pedido ou separar um produto.

- Fundo: `--cor-verde-horta`.
- Texto: `--cor-branco`.
- Hover: `--cor-verde-escuro`.
- Foco: contorno visível em `--cor-verde-escuro`.

### Secundário

Usado para ações alternativas, como voltar ou escolher outra opção.

- Fundo: `--cor-branco`.
- Texto e borda: `--cor-verde-escuro`.
- Hover: `--cor-verde-claro`.

### Ação de destaque

Usada com moderação para uma ação secundária que precise de atenção.

- Fundo: `--cor-terracota`.
- Texto: `--cor-branco`.
- Não usar como cor de todos os botões da tela.

### Estados

- Normal: ação disponível.
- Hover: mudança sutil de fundo ou borda.
- Foco: contorno de pelo menos 2px, sem remover o indicador padrão sem substituição.
- Desabilitado: menor destaque visual e sem permitir interação.
- Carregando: manter o texto da ação e indicar que a operação está em andamento.

## 3. Campos de formulário

Aplicados ao tamanho da cesta, à escolha dos produtos e à quantidade.

- Label sempre visível acima do campo.
- Fundo branco e borda neutra.
- Texto usando `--cor-texto-escuro`.
- Foco com borda ou contorno em `--cor-verde-escuro`.
- Mensagem de erro próxima do campo e também compreensível sem depender da cor.
- O campo deve ter área de toque confortável no celular.

## 4. Card de cesta

Usado para apresentar uma cesta na tela da Aline e na listagem do Vanderlei.

Deve poder mostrar:

- identificação da cesta;
- tamanho;
- situação;
- quantidade já separada e quanto ainda cabe, quando essa informação estiver disponível;
- ação para abrir os detalhes.

O card usa fundo branco, texto escuro, bordas discretas e espaçamento suficiente para leitura
rápida.

## 5. Etiqueta de situação

Sempre exibe texto junto da cor:

| Situação | Fundo | Texto |
|---|---|---|
| Pedida | `#E8F1F5` | `#2F6B8A` |
| Em separação | `#FFF1D6` | `#7A4B00` |
| Sucesso | `#E5F3E5` | `#2F7D32` |
| Erro | `#FDE8E7` | `#B42318` |

## 6. Mensagens

- Sucesso: confirma que uma ação terminou.
- Erro: explica o que não foi possível fazer e, quando possível, como corrigir.
- Vazio: informa que não há conteúdo para mostrar e orienta a próxima ação prevista.
- Carregamento: informa que os dados estão sendo buscados.

## 7. Espaçamento e forma

- Usar uma escala de 4px: 4, 8, 12, 16, 24 e 32px.
- Usar bordas arredondadas moderadas, entre 8px e 12px.
- Manter contraste e espaço em branco antes de adicionar elementos decorativos.
- Em telas de celular, priorizar uma coluna e ações com largura confortável.
- Em telas do produtor, usar o espaço horizontal para facilitar a comparação das cestas.

## 8. Ponte com o código

Os componentes React e seus estilos CSS devem usar os tokens definidos em `CORES.md` e
`TIPOGRAFIA.md`. Valores de cor, fonte, peso e tamanho não devem ser duplicados diretamente em um
componente quando já houver um token equivalente.

Antes de criar um componente novo, verificar se ele é uma variação de botão, campo, card, etiqueta
ou mensagem já definido aqui.
