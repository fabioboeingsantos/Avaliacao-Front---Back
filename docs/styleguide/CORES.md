# Styleguide de cores — Cesta do Vale

> Proposta visual baseada na cartilha e no briefing. A paleta abaixo foi ajustada para as
> combinações documentadas atenderem ao contraste AA; a identidade visual ainda precisa ser
> confirmada.

## 1. Direção visual

A paleta deve transmitir uma horta comunitária acolhedora, simples e organizada. O verde comunica
o contexto da horta; o creme deixa a leitura mais confortável; o terracota e o amarelo ajudam a
destacar ações e situações sem deixar toda a interface verde.

## 2. Paleta principal

| Nome | Uso sugerido | Hex |
|---|---|---|
| Verde horta | Cor principal, botões e elementos de destaque | `#2F6B3B` |
| Verde escuro | Títulos, textos fortes e cabeçalhos | `#1F4D2E` |
| Verde claro | Fundos suaves, seleções e áreas de apoio | `#DCEBD2` |
| Terracota | Ações secundárias e detalhes de identidade | `#A84F35` |
| Amarelo colheita | Alertas leves e situação em separação | `#E6A23C` |
| Creme natural | Fundo geral das telas | `#F7F5EF` |
| Branco | Cards, formulários e áreas de conteúdo | `#FFFFFF` |
| Texto escuro | Texto principal sobre fundos claros | `#24302A` |
| Borda suave | Bordas de campos, cards e divisões | `#CBD5CC` |

## 3. Cores de situação e feedback

As cores não devem ser o único modo de comunicar uma situação. Cada estado deve aparecer também
com texto explícito.

| Situação ou feedback | Cor sugerida | Hex | Aplicação |
|---|---|---|---|
| Pedida | Azul suave | `#2F6B8A` | Etiqueta e indicação textual da cesta pedida |
| Em separação | Amarelo colheita | `#E6A23C` | Etiqueta e indicação textual da cesta em separação |
| Sucesso | Verde sucesso | `#2F7D32` | Confirmação de ação concluída |
| Erro | Vermelho erro | `#B42318` | Mensagens de erro e validação |

Os fundos suaves usados com essas situações são `#E8F1F5`, `#FFF1D6`, `#E5F3E5` e `#FDE8E7`,
respectivamente.

## 4. Aplicação por perfil

### Aline — experiência no celular

- Fundo geral em creme natural.
- Cards e formulários em branco.
- Botão principal em verde horta.
- Destaques e ações secundárias em terracota.
- Situação da cesta sempre acompanhada do texto “pedida” ou “em separação”.

### Vanderlei — experiência no computador

- Fundo geral claro para facilitar a leitura de várias cestas.
- Filtros e controles principais em verde horta.
- Indicadores de situação com texto e cor.
- Amarelo colheita para chamar atenção ao que está em separação ou precisa de conferência.
- Vermelho erro apenas quando uma operação não puder ser realizada.

## 5. Regras de uso

- Usar verde horta como cor principal da interface.
- Usar verde escuro para textos importantes, garantindo contraste com fundos claros.
- Usar terracota com moderação, principalmente em ações secundárias e detalhes visuais.
- Usar amarelo colheita para atenção, não como cor principal de grandes áreas.
- Usar vermelho somente para erros ou situações que exigem correção.
- Não usar apenas a cor para indicar o estado de uma cesta.
- Manter contraste suficiente entre texto e fundo, principalmente no celular.
- Priorizar leitura e clareza sobre decoração.

## 6. Combinações iniciais

| Elemento | Fundo | Texto ou conteúdo |
|---|---|---|
| Tela | `#F7F5EF` | `#24302A` |
| Card | `#FFFFFF` | `#24302A` |
| Botão principal | `#2F6B3B` | `#FFFFFF` |
| Cabeçalho | `#1F4D2E` | `#FFFFFF` |
| Destaque suave | `#DCEBD2` | `#1F4D2E` |
| Etiqueta pedida | `#E8F1F5` | `#2F6B8A` |
| Etiqueta em separação | `#FFF1D6` | `#7A4B00` |
| Mensagem de erro | `#FDE8E7` | `#B42318` |

## 7. Contraste validado

Para texto normal, a referência AA usada é contraste mínimo de `4.5:1`. Para texto grande, a
referência é `3:1`. Os valores abaixo foram calculados para as combinações definidas neste
documento.

| Combinação | Contraste | Resultado |
|---|---:|---|
| Verde horta sobre branco | `6.39:1` | AA |
| Verde escuro sobre branco | `9.73:1` | AA |
| Texto escuro sobre creme natural | `12.58:1` | AA |
| Terracota sobre branco | `5.48:1` | AA |
| Azul de “pedida” sobre fundo azul claro | `5.11:1` | AA |
| Texto âmbar sobre fundo amarelo claro | `6.64:1` | AA |
| Vermelho de erro sobre fundo vermelho claro | `5.60:1` | AA |

## 8. Ponte com o código

As cores deste documento serão as mesmas usadas no CSS global do frontend. Os componentes devem
usar os tokens abaixo, sem repetir valores hexadecimais diretamente:

```css
:root {
  --cor-verde-horta: #2F6B3B;
  --cor-verde-escuro: #1F4D2E;
  --cor-verde-claro: #DCEBD2;
  --cor-terracota: #A84F35;
  --cor-amarelo-colheita: #E6A23C;
  --cor-creme-natural: #F7F5EF;
  --cor-branco: #FFFFFF;
  --cor-texto-escuro: #24302A;
  --cor-borda: #CBD5CC;
  --cor-pedida: #2F6B8A;
  --cor-texto-separacao: #7A4B00;
  --cor-sucesso: #2F7D32;
  --cor-erro: #B42318;
  --cor-fundo-etiqueta-pedida: #E8F1F5;
  --cor-fundo-etiqueta-separacao: #FFF1D6;
  --cor-fundo-sucesso: #E5F3E5;
  --cor-fundo-erro: #FDE8E7;
}
```

A tipografia seguirá a mesma regra: a família e a escala definidas em `TIPOGRAFIA.md` serão
registradas como variáveis CSS e consumidas pelos componentes.

## 9. Pendências para revisão

- [ ] Confirmar se a direção natural e acolhedora representa a Cesta do Vale.
- [ ] Confirmar a paleta principal.
- [ ] Confirmar o uso do terracota como cor secundária.
- [ ] Confirmar as cores das situações “pedida” e “em separação”.
- [x] Validar o contraste das combinações principais.
- [ ] Conferir as combinações no layout final para evitar texto sobreposto ou muito pequeno.
- [ ] Registrar a decisão final no briefing.
