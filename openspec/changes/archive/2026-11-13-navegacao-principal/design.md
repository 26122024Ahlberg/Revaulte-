# Design

## Context

Requisitos: ver `specs/navegacao-site/spec.md`. O app Reflex (`frontend/revaulte/`) tem a página `/catalogo`, a raiz `/` redirecionando para ela e um `CatalogState` que carrega `GET /vehicles` no `on_load` e guarda cartões já preparados (`CartaoVeiculo`). O topo (`topo()` em `components.py`) tem um único item.

## Goals / Non-Goals

**Goals:** uma única implementação do catálogo servindo três páginas; menu sem JavaScript próprio.

**Non-Goals:** pesquisa e filtros controlados pelo visitante (`pesquisa-filtros-catalogo`); Home (`pagina-inicial`).

## Decisions

### 1. Uma função de página parametrizada por recorte

`revaulte.py` registra `/estoque`, `/usados` e `/modificados` com a mesma estrutura de página, variando título (“Estoque”, “Usados”, “Modificados”), título da aba (“Estoque | Revaulte” etc.), mensagem de vazio e um recorte fixo. O recorte é aplicado no estado sobre a lista já recebida do Xano: `CartaoVeiculo` ganha os indicadores necessários (`usado`, além de `modificado` já existente) e o estado expõe uma variável computada com os cartões do recorte atual.

Alternativa: parâmetros de URL (`/estoque?condicao=usado`). Descartada por exigir leitura e validação de parâmetros e por gerar endereços menos legíveis na apresentação.

Alternativa: filtro no Xano (novo parâmetro no endpoint). Descartada: exige alterar o backend sem necessidade, dado o volume pequeno.

### 2. Recorte guardado no estado ao carregar a página

O `on_load` de cada rota define o recorte (`todos`, `usados`, `modificados`) antes de carregar a lista. O índice usado pela troca de imagem provisória passa a referir-se à lista exibida; a troca deve localizar o cartão pela capa e pelo identificador do veículo (acrescentar `id` ao cartão), não pela posição.

### 3. Rotas antigas e raiz provisória

`/catalogo` vira redirecionamento com `rx.redirect("/estoque", replace=True)`, no padrão já usado na raiz. A raiz deixa de redirecionar e passa a exibir uma página provisória mínima (marca, frase e botão “Ver estoque”), por decisão do usuário, para que o item Home leve a uma página própria; a Change `pagina-inicial` a substitui.

### 4. Dois grupos de navegação e um único painel

Por decisão do usuário, há dois grupos:

- **Navegação principal** (Home, Estoque, Usados, Modificados): `nav` no cabeçalho, visível acima de 760 px; oculta até 760 px.
- **Minha conta** (Meu perfil, Anunciar veículo, Meus anúncios, Favoritos, Entrar / Cadastrar): somente no painel do botão ☰, que aparece em qualquer largura no canto superior direito.

O painel é um só componente com duas seções: “Navegação” (repete os quatro itens, com a página atual marcada; exibida apenas até 760 px via CSS) e “Minha conta”. Os itens da conta são elementos de texto com `aria-disabled="true"` e o rótulo “Em breve”, sem `href` e sem evento, para não haver link quebrado nem simulação de funcionalidade.

O estado aberto/fechado fica em `MenuState.menu_aberto`. O botão alterna o estado e expõe `aria-expanded`, `aria-controls` e um `aria-label` (“Abrir menu”/“Fechar menu”). O painel fecha ao acionar um item de navegação, ao clicar na camada transparente atrás dele e no carregamento de cada página. Sem JavaScript próprio e sem animação nesta etapa.

Alternativas consideradas: menu recolhível só no celular, sem botão no desktop (versão anterior desta decisão, substituída pelo requisito de dois grupos); links da conta para uma página “Em breve” genérica (descartada: criaria páginas vazias apresentadas como funcionalidade).

### 5. Página não encontrada

Usar o recurso de página 404 do Reflex com a estrutura `pagina()` existente, mensagem e link para `/estoque`. Confirmar na versão 0.10 a forma de registrar a página 404 personalizada; se não houver, manter a padrão e registrar a limitação.

## Risks / Trade-offs

- [Troca de imagem provisória ligada à posição do cartão] → passar a identificar o cartão pelo `id` do veículo (decisão 2).
- [Mudança de rota quebra o endereço `/catalogo` já conferido] → redirecionamento mantido e testado.
- [Página 404 personalizada não suportada na versão fixada] → confirmado: o Reflex 0.10 aceita `add_page(..., route="404")`.
- [“Anunciar veículo” e “Meus anúncios” não estão previstos em `docs/project-overview.md` nem em `docs/domain-model.md`, onde os veículos são anunciados pela loja na área administrativa] → os itens aparecem apenas como “Em breve”, sem rota; antes de especificar essas funcionalidades, confirmar com o usuário se o cliente poderá anunciar e atualizar a documentação.
