# Validação do pacote

## Revisão de 16/11/2026

As referências foram atualizadas a partir do checkout local baseado no commit `22d3fbd`.
Consultar [ESTADO_ATUAL.md](ESTADO_ATUAL.md) para os comportamentos conferidos e as alterações
locais pendentes de commit.

O manifesto passou de 57 para 69 entradas. Foram conferidas a integridade das 68 cópias sincronizadas
por SHA-256 e a correspondência com as origens. A entrada do exemplo de ambiente conserva
seu hash anterior e foi excluída da leitura e da sincronização.

Foram conferidos 34 links locais do índice, dos cinco modelos, do roteiro de hackathon e do documento de estado atual,
todos com destinos existentes.
Esta revisão documental utiliza a inspeção da configuração Vite para registrar a permanência
do bloqueio `**/CRIACAO_NOVO_SISTEMA/**`. A evidência HTTP abaixo pertence à execução de 10/11.

## Evidências históricas de 10/11/2026

Verificações executadas em **10/11/2026**:

- 57 cópias conferidas pelo SHA-256 registrado no manifesto.
- 16 links locais do índice/modelos novos conferidos, sem destinos ausentes.
- Blocos de código dos documentos novos conferidos, sem fechamento ausente.
- `npm run lint` e `npm run build` do frontend aprovados após a configuração de bloqueio.
- Servidor Vite temporário encerrado após o teste: acesso direto ao documento por `/@fs/`
  retornou **403**; `isFileLoadingAllowed` retornou `false`.
- A URL comum `/CRIACAO_NOVO_SISTEMA/00_COMECE_AQUI.md` retornou o fallback da aplicação,
  sem o conteúdo do documento. HTTP 200 do fallback não significa publicação do arquivo.
- A página inicial continuou respondendo HTTP 200.

Os testes verificam a configuração local. Não houve deploy ou consulta à hospedagem nesta tarefa.
Os links herdados das referências para código/imagens que não fazem parte deste pacote não são
considerados documentos autossuficientes; a limitação está explicada no índice.
