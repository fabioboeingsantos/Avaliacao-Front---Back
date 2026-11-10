# Cenários de validação da IA

Testes automatizados em `backend/tests/ia/`, sem chamadas reais:

- `test_openrouter.py`: três etapas, modelos por papel, contexto autorizado,
  JSON estrito, aprovação QA, falhas do provedor e rejeição de modelos pagos.
- `test_fluxo.py`: aprovação indevida do modelo não supera tamanho ausente em cesta pronta,
  produto inexistente, exclusão contraditória, conflito de limite por tamanho ou operação proibida ao perfil;
  preserva motivos específicos e dúvidas do QA em proposta nula e valida cálculo automático na cesta selecionável.
- `test_isolamento.py`: modo simulado recebe apenas as cestas autorizadas e respeita exclusões.

Execute na raiz com `.\.venv-tests\Scripts\python.exe -m pytest backend/tests/ia -q`.
Para toda a API: `.\.venv-tests\Scripts\python.exe -m pytest backend/tests -q`.

As evidências históricas das chamadas reais e as limitações do QA continuam em
[TESTES_ASSISTENTE_OPENROUTER.md](../TESTES_ASSISTENTE_OPENROUTER.md).

A refatoração não implementa memória entre mensagens nem corrige as limitações
registradas do QA. Consulte [arquitetura](arquitetura.md) para distinguir o fluxo atual
do fluxograma de evolução com estado.
