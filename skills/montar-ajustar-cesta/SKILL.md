---
name: montar-ajustar-cesta
description: Montar, alterar ou repetir uma cesta do assinante na Flora, preservando contexto, quantidades e exclusões e aplicando as regras atuais do backend.
---

# Montar e ajustar cesta

Use esta skill ao trabalhar no comportamento do agente Assinante para pedidos de montagem, alteração ou repetição de cestas.

Leia as [instruções operacionais](../../backend/ia/prompts/skills/montar-ajustar-cesta.md), que são a fonte única do procedimento. Elas ficam no pacote do backend para acompanhar os deploys em Docker e Vercel. O carregador `backend/ia/prompts/__init__.py` inclui esse conteúdo na instrução do agente Assinante.

Use os contratos de `backend/ia/contratos.py` e as regras fornecidas no contexto do backend. Ao ajustar a skill, confira a montagem do contexto em `backend/ia/fluxo.py` e as validações em `backend/ia/validacao.py`.
