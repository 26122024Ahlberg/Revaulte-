# Proposal

## Why

Com o estoque crescendo, o visitante precisa encontrar rapidamente um modelo específico ou restringir a lista a usados, novos, originais ou modificados. A visão geral prevê filtros básicos do catálogo; para o MVP, priorizam-se pesquisa por texto e os filtros que expressam a especialidade da Revaulte.

## What Changes

- Campo de pesquisa por marca, modelo e versão nas páginas de estoque, sem diferenciar maiúsculas, minúsculas e acentos.
- Filtro por condição (Todos, Novo, Usado) e por modificação (Todos, Modificados, Originais), usando os campos `condition` e `is_modified` já existentes.
- Combinação da pesquisa com os filtros e com o recorte fixo das páginas `/usados` e `/modificados`.
- Mensagem de nenhum resultado com a ação “Limpar filtros”.
- Atualização da documentação para incluir o filtro por modificação entre os filtros do catálogo.

### Fora do escopo

- Filtros por ano e faixa de preço, ordenação escolhida pelo visitante e paginação (previstos na visão geral, ficam para uma Change posterior).
- Persistência dos filtros na URL ou entre visitas.
- Alterações no backend Xano.

## Capabilities

### New Capabilities

- `pesquisa-catalogo`: pesquisa por texto e filtros de condição e modificação nas páginas de estoque.

### Modified Capabilities

Nenhuma.

## Impact

- **Frontend Reflex**: estado do catálogo (texto e filtros, variável computada dos cartões exibidos), componentes do formulário de pesquisa e filtros, estilos.
- **Backend Xano**: nenhum; filtragem sobre a lista já recebida de `GET /vehicles`.
- **Documentação**: `docs/project-overview.md` e `docs/domain-model.md` (filtro por modificação).
- **Dependências**: depois de `navegacao-principal` (recortes de Usados e Modificados).
