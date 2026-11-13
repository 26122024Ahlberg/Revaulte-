# Tasks

## 1. Lógica de filtragem

- [x] 1.1 Implementar `filtrar_cartoes` e a normalização de texto em `state.py`, e as variáveis de pesquisa e filtros no `CatalogState` com reinício no `on_load`; verificar com testes em `frontend/tests/` (pesquisa por modelo, sem acento, vazia, combinação com filtros e recortes, vendido filtrável, nenhum resultado)

## 2. Interface

- [x] 2.1 Implementar em `components.py` o campo de pesquisa com atraso de digitação, os filtros com rótulos conforme a página, a mensagem de nenhum resultado e “Limpar filtros”; verificar no navegador cada cenário de `specs/pesquisa-catalogo/spec.md` — implementado; testes de componente passam e a filtragem foi conferida com os 3 veículos reais do Xano; cenários da spec confirmado pelo usuário no Safari (desktop) em 27/10/2026
- [x] 2.2 Estilizar os controles em `styles.css` na identidade da Revaulte e em 980 e 560 px; verificar no navegador nas três larguras e navegação por teclado — implementado (campos com quebra de linha; uma coluna até 560 px); aparência no desktop confirmado pelo usuário no Safari (desktop) em 27/10/2026; pendente 980 e 560 px e navegação por teclado — verificado em 13/11/2026 no Safari 26 do macOS, por automação WebDriver (`safaridriver`) sobre o servidor local, com medições registradas: a 980 px os três campos ficam em uma linha e a 560 px em uma coluna, sem rolagem horizontal nem elementos fora da tela; pelo teclado, Tab percorre pesquisa e filtros, a pesquisa “gol” resulta em “1 veículo”, “Limpar filtros” é acionado com Enter e o foco é visível (contorno vermelho de 2 px)

## 3. Documentação e verificação

- [x] 3.1 Incluir o filtro por modificação em `docs/project-overview.md` (seção 6) e em `docs/domain-model.md` (seção 12); verificar o texto
- [x] 3.2 Executar os testes, `reflex compile` e `openspec validate pesquisa-filtros-catalogo --strict`; verificar que passam e que `xano/` e `frontend-html/` não foram alterados — verificado em 21/10/2026 na auditoria do OpenSpec: 97 testes, `reflex compile` e `openspec validate --all --strict` passam; `git diff` sem alterações em `xano/` e `frontend-html/`
