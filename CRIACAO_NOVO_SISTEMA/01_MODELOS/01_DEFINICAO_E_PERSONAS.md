# Definição e personas do novo sistema

Status: modelo a preencher. Campos entre colchetes exigem uma decisão.

## Identificação

- Nome do sistema: [preencher].
- Responsável e data: [preencher].
- Problema que será resolvido: [preencher].
- Como o processo funciona hoje: [preencher].
- Resultado esperado e indicador de sucesso: [preencher].
- Público e contexto de uso: [preencher].

## Mapa de adaptação

| Referência anterior | Nova persona | Novo perfil técnico | Responsabilidade equivalente? |
| --- | --- | --- | --- |
| Aline / assinante | [nome] | [perfil] | [sim/não; diferenças] |
| Vanderlei / produtor | [nome] | [perfil] | [sim/não; diferenças] |
| Flora / assistente opcional | [nome ou remover] | Não é conta de usuário | [operações permitidas] |

A persona descreve uma pessoa representativa; o perfil técnico determina suas permissões.
Mudar o nome de uma persona não exige mudar uma chave técnica. Mudar suas responsabilidades exige
revisar permissões, dados e regras, mesmo que o nome técnico do perfil seja mantido.

## Ficha de cada persona

Duplique este bloco para cada persona:

- Nome e descrição: [preencher].
- Objetivos: [preencher].
- Dificuldades atuais: [preencher].
- Tarefas principais: [preencher].
- Dispositivos, conectividade e necessidades de acessibilidade: [preencher].
- Dados que consulta: [preencher].
- Dados que cria ou altera: [preencher].
- Operações que não pode realizar: [preencher].
- Situações de erro e como precisa recuperar o trabalho: [preencher].

## Matriz de permissões

| Operação | Perfil A | Perfil B | Restrição de propriedade/estado |
| --- | --- | --- | --- |
| Consultar registros | [sim/não] | [sim/não] | [próprios/todos/outro] |
| Criar registro | [sim/não] | [sim/não] | [condições] |
| Atualizar registro | [sim/não] | [sim/não] | [condições] |
| Cancelar registro | [sim/não] | [sim/não] | [condições] |
| Concluir operação | [sim/não] | [sim/não] | [condições] |
| Gerenciar catálogo ou equivalente | [sim/não] | [sim/não] | [condições] |

## Escopo da troca

- [ ] Somente nomes, biografias e imagens; responsabilidades preservadas.
- [ ] Identidade visual e linguagem também mudam.
- [ ] Mudam tarefas, entidades ou regras; adaptar o domínio antes de reutilizar o código.

Registrar a decisão: [preencher].
