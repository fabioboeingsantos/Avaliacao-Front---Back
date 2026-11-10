# Requisitos e fluxos do novo sistema

Preencha após [definir as personas](01_DEFINICAO_E_PERSONAS.md).

## Escopo

- Funcionalidades do primeiro lançamento: [preencher].
- Itens fora do escopo: [preencher].
- Funcionalidades futuras, sem compromisso de implementação: [preencher].

## Funcionalidades e aceite

| ID | Persona/perfil | Necessidade | Comportamento esperado | Critério de aceite verificável |
| --- | --- | --- | --- | --- |
| RF-01 | [perfil] | [necessidade] | [ação e resultado] | [dado/quando/então] |

## Jornada de cada perfil

1. Entrada e autenticação: [preencher].
2. Consulta dos dados permitidos: [preencher].
3. Preparação da ação principal: [preencher].
4. Revisão e confirmação: [preencher].
5. Persistência e retorno: [preencher].
6. Acompanhamento e conclusão: [preencher].
7. Cancelamento/correção e falhas: [preencher].

## Estados e transições

| Estado inicial | Ação | Perfil autorizado | Condição | Próximo estado | Efeito nos dados |
| --- | --- | --- | --- | --- | --- |
| [estado] | [ação] | [perfil] | [validação] | [estado] | [efeito] |

Para cada transição, definir como impedir repetição ou conflito de requisições simultâneas.
Não herdar automaticamente prazos, limites 5/8/12, unidades, categorias ou estados do Cesta do Vale.

## Dados

| Entidade | Campos essenciais | Relacionamentos | Restrições | Quem pode acessar |
| --- | --- | --- | --- | --- |
| Conta | [campos] | [relações] | [unicidade] | [escopo] |
| [entidade do novo domínio] | [campos] | [relações] | [validações] | [escopo] |

## Requisitos técnicos

- Política de sessão, expiração e logout: [preencher].
- Isolamento de dados entre contas: [preencher].
- Recuperação de senha/e-mail: [necessário ou não].
- Limitação de requisições e múltiplas instâncias: [preencher].
- Responsividade e acessibilidade: [preencher].
- Backups, logs e recuperação de falhas: [preencher].

## Assistente opcional

- Manter ou remover: [decisão].
- Nome, linguagem e público: [preencher].
- Consultas e ações permitidas por perfil: [preencher].
- Ações que exigem confirmação explícita: [preencher].
- Provedor, limites e custos: [preencher].
- Histórico, voz e alternativa manual: [preencher].

O assistente não deve substituir autenticação, autorização ou validação determinística da API.
