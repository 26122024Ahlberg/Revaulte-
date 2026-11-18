# Design

## Context

Motivação e escopo: ver `proposal.md`. Requisitos: ver `specs/visual-paginas-internas/spec.md`.

As páginas de estoque (`/estoque`, `/usados` e `/modificados`) e a página do veículo compartilham `styles.css` com a Home. A Home já tem o carrossel fotográfico e não pode mudar. O conteúdo e o comportamento (pesquisa, filtros, simulador, estados de carregamento) vêm de Changes anteriores e também não podem mudar. As regras de movimento da Change `animacoes-interface` continuam valendo: entradas curtas e nada de animação de entrada, deslocamento ou rotação com movimento reduzido.

## Goals / Non-Goals

**Goals:**
- Concentrar o novo acabamento em classes próprias das páginas internas, para que a Home não seja afetada.
- Usar fotografia sem prejudicar a leitura, inclusive quando a imagem não carrega.
- Manter o custo de renderização aceitável em celular.

**Non-Goals:**
- Novos componentes de comportamento, novos estados ou mudanças no backend.
- Gestão de imagens no Xano: os banners são arquivos estáticos em `frontend/assets/`.

## Decisions

### 1. Escopo por classes de invólucro

`pagina_estoque` envolve o banner e o catálogo em `div.inner-page`; a página do veículo usa `div.inner-page.inner-vehicle`. Todo o CSS novo é escrito sob `.inner-page`, `.page-banner`, `.vehicle-backdrop` e `.inner-vehicle`. Assim a Home, que não recebe essas classes, continua igual, o que é conferido por teste. Alternativa descartada: alterar as regras globais de `.card` e de fundo, que mudariam também os destaques da Home.

### 2. Banner com `<img>` decorativo e dados em uma tabela

`banner_interno` monta uma `section.page-banner is-<chave>` com a foto (`img` com `alt=""` e `aria-hidden`), uma camada de escurecimento e o conteúdo (`h1` com o título da página e texto curto). A foto, o texto e a chave de cada página ficam em `BANNERS_ESTOQUE` em `components.py`. Com `img` em vez de `background-image`, o caminho da foto fica no componente, onde os testes conferem que cada página tem foto própria, diferente das da Home e com menos de 420 KB. O enquadramento de cada foto é ajustado no CSS pela classe `is-<chave>` (`object-position`).

O banner tem fundo escuro próprio (`#0d0d0f`), e o texto fica sobre a camada de escurecimento: se a foto não carregar, o título e o texto continuam legíveis.

### 3. Foto à direita no computador, largura total no celular

No computador, a foto ocupa cerca de 72% da largura à direita e esmaece para o preto à esquerda (`mask-image`), onde fica o texto: o carro não fica sob o título. Até 760 px, a foto ocupa a largura toda, o texto vai para baixo e o escurecimento fica mais forte. A altura usa `clamp(250px, 38vh, 400px)`, para não ocupar a tela inteira. Alternativa descartada: foto de fundo inteira com uma camada uniforme, que deixava o carro sob o texto ou escuro demais.

### 4. Página do veículo com a própria capa ao fundo

`fundo_veiculo` reaproveita a capa do anúncio como fundo desfocado (`filter: blur`, opacidade 0,28), exibido só quando o veículo foi encontrado e a capa não é a imagem provisória. Não há nenhuma imagem nova, e o fundo combina com o veículo exibido. A ficha técnica vira uma grade de blocos, e os painéis de descrição, modificações e simulador recebem o mesmo acabamento, somente por CSS sob `.inner-vehicle`.

### 5. Movimento: entradas curtas, efeitos decorativos longos e movimento reduzido

As entradas de conteúdo usam `revaulte-rise` (0,4 s, atraso de até 0,2 s), dentro do limite de `animacoes-interface`. Efeitos puramente decorativos podem ser mais longos (zoom do banner de 1,2 s, aparecimento do fundo desfocado de 0,8 s e névoa vermelha contínua de 14 s), porque não atrasam a leitura do conteúdo.

Com `prefers-reduced-motion: reduce`, a regra global desativa animações e transições de todos os elementos e também dos pseudo-elementos (`*, *::before, *::after`). Isso é necessário porque a névoa é um pseudo-elemento (`.inner-page > .catalog::before`), que o seletor `*` sozinho não alcança. O teste `test_movimento_reduzido_alcanca_pseudoelementos` em `tests/test_animacoes.py` impede que essa cobertura seja perdida.

### 6. Custo em celular

Até 560 px, o desfoque do fundo do veículo e da névoa fica mais leve e o `backdrop-filter` da barra de filtros é removido, porque desfoque pesado custa caro em celulares.

## Risks / Trade-offs

- [O `overflow: hidden` de `.inner-page`, necessário para os elementos decorativos maiores que a tela (fundo desfocado a 110%, névoa), pode esconder conteúdo cortado em vez de mostrar rolagem horizontal] → verificar em telas estreitas que não há texto cortado, além de não haver rolagem; a coluna única do simulador usa `minmax(0, 1fr)` para poder encolher abaixo da largura do conteúdo.
- [Desfoque e gradientes aumentam o custo de pintura] → versão mais leve até 560 px e animações só em `opacity` e `transform`.
- [Se a capa externa do anúncio falhar, o fundo desfocado não aparece] → aceitável: é decorativo (`alt=""`, `aria-hidden`), e a foto principal já troca para a imagem provisória.
- [Fotos de terceiros] → fotos do Pexels de uso livre, com créditos e licença registrados em `frontend/README.md`.
