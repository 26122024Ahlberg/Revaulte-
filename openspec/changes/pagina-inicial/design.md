# Design

## Context

Requisitos: ver `specs/pagina-inicial/spec.md`. O `GET /vehicles` devolve Disponíveis e Vendidos ordenados por `created_at` decrescente; o estado do catálogo já faz a requisição, a preparação dos cartões e o tratamento de erro. `frontend-rascunho/` tem um hero com slider e uma faixa de diferenciais que serve de referência visual, mas cujas afirmações (“Procedência garantida”, “Laudo cautelar”, “Financiamento facilitado”) não estão definidas na documentação.

## Goals / Non-Goals

**Goals:** reaproveitar requisição, preparação e cartões do catálogo; banner sem dependência de serviço externo durante a apresentação.

**Non-Goals:** slider, vídeo, critério administrativo de destaque.

## Decisions

### 1. Destaques como recorte do catálogo

O `CatalogState` já carrega `GET /vehicles` (do mais recente para o mais antigo) e aplica recortes por página (`todos`, `usados`, `modificados`). Os destaques entram como mais um recorte, `destaques`: os 3 primeiros cartões não vendidos da lista. A Home usa a mesma região de estados (carregando, lista, vazio, erro com “Tentar novamente”) com a mensagem própria “Não há destaques no momento.”. Nenhuma requisição ou conversão é duplicada.

Alternativa: campo `is_featured` no Xano. Descartada nesta Change por decisão do usuário (exige mudança no backend e na futura administração).

Alternativa: estado próprio da Home. Descartada: duplicaria carga e tratamento de erro sem ganho, já que só uma página fica aberta por vez.

### 2. Carrossel com estado no Reflex e imagens locais

O banner é um carrossel de três slides fixos (esportivo, modificado, clássico). O slide visível fica em `CarrosselState.indice`, alterado pelos eventos `anterior`, `proximo` (circulares) e `ir_para`, e reiniciado em 0 no carregamento da Home. Os três slides são renderizados juntos e sobrepostos; o ativo recebe a classe `is-active`. Os inativos ficam com `visibility: hidden` e `aria-hidden`, o que também os retira da ordem de foco. A troca é um esmaecimento em CSS (`opacity`), anulado pela regra de movimento reduzido.

Acessibilidade: a seção tem `aria-roledescription="carrossel"` e rótulo; cada slide tem `aria-roledescription="slide"` e rótulo “N de 3”; a região dos slides tem `aria-live="polite"`; setas e indicadores são botões com `aria-label`, e o indicador ativo tem `aria-current`. Há um `h1` visualmente oculto com o nome da Revaulte, e os títulos dos slides são `h2`.

Sem rotação automática: exigiria um temporizador por visitante e um controle de pausa para atender às diretrizes de acessibilidade; a troca manual é a prioridade definida pelo usuário.

Imagens (todas do Pexels, marcadas como “Free” e regidas pela licença do Pexels, https://www.pexels.com/license/: uso gratuito em sites, sem atribuição obrigatória, sem venda de cópias inalteradas, sem uso como marca e sem sugerir endosso de marcas), salvas localmente com até 1920 px de largura e no máximo cerca de 400 KB cada:

| Slide | Arquivo | Foto | Autor |
| --- | --- | --- | --- |
| Esportivo | `hero-esportivo.jpg` | https://www.pexels.com/photo/red-car-driving-on-road-along-fence-3466513/ (esportivo vermelho em movimento à beira-mar) | Abdulwahab Alawadhi |
| Modificado | `hero-modificado.jpg` | https://www.pexels.com/photo/modified-audi-s4-9661333/ (Audi rebaixado em garagem) | Erik Mclean |
| Clássico | `hero-classico.jpg` | https://www.pexels.com/photo/vintage-red-sports-car-by-scenic-roadside-38058755/ (esportivo clássico vermelho) | Seppo Vänni |

Nenhuma das fotos mostra pessoas identificáveis ou placas legíveis. O usuário preferia uma Porsche vermelha em movimento com praia ou montanha no slide esportivo; não foi encontrada no Pexels foto com essas condições e licença verificável. O slide esportivo usa um esportivo vermelho em movimento à beira-mar, e a Porsche vermelha (356) aparece no slide clássico. O crédito fica no `frontend/README.md`, por cortesia. A foto única usada antes (`hero.jpg`) é removida.

Alternativa: URLs externas. Descartada para não depender da rede de terceiros durante a apresentação.

### 3. Animações leves só em CSS

Entrada do texto do banner e das seções com `opacity` e `transform` (até 0,6 s), com atraso curto entre elementos; troca de slide por esmaecimento de 0,7 s. A regra `prefers-reduced-motion: reduce` existente passa a desativar também `animation`. As animações das demais páginas continuam na Change `animacoes-interface`.

### 4. Texto da proposta

Texto institucional curto sobre a curadoria de antigos, clássicos, esportivos e preparados e sobre a apresentação transparente da configuração original e das modificações (já prevista na visão geral). Sem diferenciais de serviço não definidos. O texto é revisado pelo usuário antes de concluir a tarefa.

### 5. Substituição da página provisória

A rota `/` passa a renderizar a Home completa no lugar da página provisória da Change `navegacao-principal`; o requisito correspondente de `navegacao-site` é removido nesta Change.

## Risks / Trade-offs

- [Três imagens pesadas atrasam a primeira exibição] → arquivos reduzidos (até ~400 KB) e fundo escuro imediato.
- [Marcas visíveis nos carros das fotos] → uso apenas ilustrativo, sem sugerir parceria ou endosso das montadoras.
- [Duas páginas carregando a mesma lista] → aceitável para o volume; nenhuma alteração no backend.
- [Texto institucional promete o que a loja não oferece] → restrição explícita na spec e revisão do usuário.
