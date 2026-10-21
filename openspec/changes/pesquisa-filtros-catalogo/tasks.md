# Tasks

## 1. Lógica de filtragem

- [ ] 1.1 Implementar `filtrar_cartoes` e a normalização de texto em `state.py`, e as variáveis de pesquisa e filtros no `CatalogState` com reinício no `on_load`; verificar com testes em `frontend/tests/` (pesquisa por modelo, sem acento, vazia, combinação com filtros e recortes, vendido filtrável, nenhum resultado)

## 2. Interface

- [ ] 2.1 Implementar em `components.py` o campo de pesquisa com atraso de digitação, os filtros com rótulos conforme a página, a mensagem de nenhum resultado e “Limpar filtros”; verificar no navegador cada cenário de `specs/pesquisa-catalogo/spec.md`
- [ ] 2.2 Estilizar os controles em `styles.css` na identidade da Revaulte e em 980 e 560 px; verificar no navegador nas três larguras e navegação por teclado

## 3. Documentação e verificação

- [ ] 3.1 Incluir o filtro por modificação em `docs/project-overview.md` (seção 6) e em `docs/domain-model.md` (seção 12); verificar o texto
- [ ] 3.2 Executar os testes, `reflex compile` e `openspec validate pesquisa-filtros-catalogo --strict`; verificar que passam e que `xano/` e `frontend-html/` não foram alterados
