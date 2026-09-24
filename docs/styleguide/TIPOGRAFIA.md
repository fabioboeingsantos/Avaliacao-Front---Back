# Styleguide de tipografia — Cesta do Vale

> A tipografia precisa ser simples, legível no celular e consistente no computador. Não será
> adicionada uma biblioteca de fontes: o sistema usará fontes disponíveis no próprio aparelho.

## 1. Família tipográfica

```css
--fonte-principal: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
```

Essa escolha evita dependência externa, mantém o carregamento rápido para Aline no celular e usa a
fonte nativa mais adequada em cada sistema operacional.

## 2. Pesos

| Token | Valor | Uso |
|---|---:|---|
| `--peso-regular` | `400` | Textos corridos e descrições |
| `--peso-medio` | `500` | Texto de apoio e controles |
| `--peso-semi` | `600` | Labels, botões e títulos menores |
| `--peso-negrito` | `700` | Títulos principais e valores importantes |

## 3. Escala de texto

| Token | Tamanho | Linha | Uso |
|---|---:|---:|---|
| `--texto-pequeno` | `0.75rem` / 12px | 1rem / 16px | Legendas e apoio |
| `--texto-rotulo` | `0.875rem` / 14px | 1.25rem / 20px | Labels e etiquetas |
| `--texto-base` | `1rem` / 16px | 1.5rem / 24px | Texto principal e campos |
| `--texto-grande` | `1.125rem` / 18px | 1.75rem / 28px | Destaques e introduções |
| `--titulo-3` | `1.25rem` / 20px | 1.75rem / 28px | Títulos de cards |
| `--titulo-2` | `1.5rem` / 24px | 2rem / 32px | Títulos de seção |
| `--titulo-1` | `2rem` / 32px | 2.5rem / 40px | Título principal |

No celular, o título principal pode usar `1.75rem` / 28px com linha de `2.25rem` / 36px para
preservar espaço sem prejudicar a leitura.

## 4. Regras de uso

- O texto principal deve usar `--texto-base`.
- Títulos devem usar os pesos `600` ou `700`.
- Labels devem permanecer próximos dos campos que descrevem.
- Não usar caixa alta em parágrafos ou mensagens longas.
- Não comunicar estado apenas com peso, tamanho ou cor.
- O texto deve continuar legível quando ampliado.

## 5. Ponte com o código

Os tokens abaixo serão declarados no CSS global e usados pelos componentes React:

```css
:root {
  --fonte-principal: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --peso-regular: 400;
  --peso-medio: 500;
  --peso-semi: 600;
  --peso-negrito: 700;
  --texto-pequeno: 0.75rem;
  --texto-rotulo: 0.875rem;
  --texto-base: 1rem;
  --texto-grande: 1.125rem;
  --titulo-3: 1.25rem;
  --titulo-2: 1.5rem;
  --titulo-1: 2rem;
}
```

As telas não devem definir outra família tipográfica ou tamanhos fora desta escala sem uma
justificativa registrada no briefing.
