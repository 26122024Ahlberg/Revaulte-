# Tasks

> **Atualização (26/11/2026):** tarefa 2.2 verificada no navegador; todas as tarefas concluídas. O cenário de destaque editorial Vendido tem somente cobertura automatizada (não há veículo Vendido no Xano).

> **Situação (24/11/2026):** implementação e testes locais concluídos (435 testes; `reflex compile --dry` com sucesso; `openspec validate destaques-editoriais --strict`). Sem commit. A tarefa 2.2 (Home em 6, 5 e 4 no navegador) depende da inserção dos veículos novos no Xano.

## 1. Frontend
- [x] 1.1 Acrescentar `IDS_DESTAQUES` e o parâmetro `ids_destaque` em `aplicar_recorte` (`frontend/revaulte/state.py`), sem alterar os demais recortes
- [x] 1.2 Testes: três presentes, um indisponível (Vendido), ausentes, lista vazia e ordem; atualizar os testes antigos dos destaques para não depender dos ids reais
- [x] 1.3 Executar a suíte completa e `reflex compile --dry`

## 2. Documentação e verificação
- [x] 2.1 Atualizar `docs/domain-model.md`, `docs/project-overview.md` e `docs/expansao-estoque.md` com a regra de destaques
- [x] 2.2 Depois da inserção dos veículos novos no Xano, confirmar no navegador que a Home mostra 6, 5 e 4 e que o Estoque segue do mais novo para o mais antigo — **Concluída em 26/11/2026** (verificação automatizada em 26/11/2026, em Edge sem janela, como visitante, em `localhost:3001` (roteiro e capturas temporários, não versionados)): a Home exibe, nesta ordem, os veículos 6, 5 e 4 (1280, 560 e 375 px) e `/estoque` lista 13, 12, 11, 10, 9, 8, 6, 5, 4, 3, 2 e 1, do mais novo para o mais antigo, com os veículos 8 a 13 já inseridos no Xano; console sem erros.
- [x] 2.3 `openspec validate destaques-editoriais --strict`

## Workflow follow-up
- Commit, push e archive somente com autorização do usuário.
