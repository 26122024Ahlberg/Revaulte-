# Design

## Context

Requisitos: ver `specs/pesquisa-catalogo/spec.md`. Após `navegacao-principal`, o `CatalogState` guarda a lista completa de cartões e um recorte fixo por página, expondo uma variável computada com os cartões exibidos.

## Goals / Non-Goals

**Goals:** filtragem no servidor do Reflex sobre a lista já carregada; lógica de filtragem em funções puras testáveis.

**Non-Goals:** filtros por ano e preço, ordenação, filtros na URL.

## Decisions

### 1. Filtro em funções puras, com o recorte aplicado separadamente

Duas funções puras em `state.py`:

- `aplicar_recorte(cartoes, recorte)` aplica o recorte fixo da página (`todos`, `usados`, `modificados`; também `destaques`, usado pela página inicial);
- `filtrar_cartoes(cartoes, busca, condicao, modificacao)` aplica a pesquisa e os filtros escolhidos pelo visitante.

A variável computada `cartoes_exibidos` do `CatalogState` as encadeia sobre a lista completa já carregada: primeiro o recorte, depois a pesquisa e os filtros. O recorte fica separado para ser reutilizado nos destaques da página inicial e para que cada etapa seja testada isoladamente; o resultado é o mesmo de exigir todas as condições ao mesmo tempo.

A normalização (`normalizar_texto`) usa `unicodedata` (remoção de acentos) e `casefold()` e reduz espaços repetidos a um só. A pesquisa procura o termo normalizado como trecho do título já preparado (marca, modelo e versão, nessa ordem), de modo que um termo pode abranger mais de um campo (“chevrolet opala”). Biblioteca padrão; nenhuma dependência nova.

### 2. Controles do Reflex

Campo de pesquisa `rx.el.input` com atraso de digitação por `rx.debounce_input` (300 ms, confirmado no Reflex 0.10) para não enviar um evento por tecla; filtros com `rx.el.select` nativo, rotulados com `label` para acessibilidade. A barra é um `div` com `role="search"` (sem `form`, para não haver envio), fica fora da região `aria-live` do catálogo (`#catalog-region`) e mostra a contagem de veículos exibidos em um parágrafo próprio com `aria-live="polite"`, para que leitores de tela anunciem a nova contagem ao mudar a pesquisa ou um filtro. Estilos com as variáveis de cor da Revaulte em `styles.css`.

### 3. Estados da página

A região do catálogo passa a distinguir “catálogo vazio” (backend sem veículos) de “nenhum resultado” (filtros excluíram tudo). Os filtros ficam visíveis só quando a lista foi carregada com sucesso.

### 4. Reinício ao trocar de página

Ao abrir `/estoque`, `/usados` ou `/modificados`, a pesquisa e os filtros são reiniciados no `on_load`, para que um filtro de uma página não esconda veículos na outra.

## Risks / Trade-offs

- [Um evento por tecla sobrecarrega o WebSocket] → atraso de digitação.
- [Filtrar no servidor do Reflex não escala para estoques grandes] → aceitável para o volume; paginação e filtro no backend ficam para a Change de ordenação e filtros avançados.
