# Validação do pacote

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
