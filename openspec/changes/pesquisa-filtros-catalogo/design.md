# Design

## Context

Requisitos: ver `specs/pesquisa-catalogo/spec.md`. Após `navegacao-principal`, o `CatalogState` guarda a lista completa de cartões e um recorte fixo por página, expondo uma variável computada com os cartões exibidos.

## Goals / Non-Goals

**Goals:** filtragem no servidor do Reflex sobre a lista já carregada; lógica de filtragem em funções puras testáveis.

**Non-Goals:** filtros por ano e preço, ordenação, filtros na URL.

## Decisions

### 1. Filtro em função pura

`filtrar_cartoes(cartoes, texto, condicao, modificacao, recorte)` em `state.py`, chamada pela variável computada. A normalização do texto usa `unicodedata` (remoção de acentos) e `casefold()`, comparando com o título já preparado (marca, modelo e versão). Biblioteca padrão; nenhuma dependência nova.

### 2. Controles do Reflex

Campo de pesquisa com `rx.input` (ou `rx.el.input`) com atraso de digitação (`rx.debounce_input` ou `debounce_timeout`, confirmar no Reflex 0.10) para não enviar um evento por tecla; filtros com `rx.el.select` nativo, rotulados com `label` para acessibilidade. Estilos com as variáveis de cor da Revaulte em `styles.css`.

### 3. Estados da página

A região do catálogo passa a distinguir “catálogo vazio” (backend sem veículos) de “nenhum resultado” (filtros excluíram tudo). Os filtros ficam visíveis só quando a lista foi carregada com sucesso.

### 4. Reinício ao trocar de página

Ao abrir `/estoque`, `/usados` ou `/modificados`, a pesquisa e os filtros são reiniciados no `on_load`, para que um filtro de uma página não esconda veículos na outra.

## Risks / Trade-offs

- [Um evento por tecla sobrecarrega o WebSocket] → atraso de digitação.
- [Filtrar no servidor do Reflex não escala para estoques grandes] → aceitável para o volume; paginação e filtro no backend ficam para a Change de ordenação e filtros avançados.
