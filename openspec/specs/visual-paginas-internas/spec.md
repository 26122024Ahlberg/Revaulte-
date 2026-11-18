# visual-paginas-internas Specification

## Purpose
Define a apresentação visual das páginas internas da Revaulte (estoque e página do veículo), alinhada à identidade de marketplace premium da Home, sem alterar conteúdo nem comportamento.

## Requirements

### Requirement: Banner das páginas de estoque
As páginas `/estoque`, `/usados` e `/modificados` SHALL exibir no topo um banner horizontal com fotografia automotiva escurecida e decorativa, o título da página como título principal e um texto curto. O banner MUST NOT ocupar a altura inteira da tela. Cada página SHALL usar fotografia própria, diferente das do carrossel da Home, com o carro inteiro e fora de baixo do texto em telas de computador. O título SHALL continuar legível se a fotografia não carregar.

#### Scenario: Visitante abre o estoque
- **WHEN** o visitante abre `/estoque`
- **THEN** o banner com fotografia e o título “Estoque” aparecem acima da pesquisa e da listagem

#### Scenario: Fotografia indisponível
- **WHEN** a fotografia do banner não carrega
- **THEN** o título e o texto continuam legíveis sobre o fundo escuro

### Requirement: Página do veículo valorizando a fotografia
A página do veículo SHALL destacar a foto principal do anúncio e apresentar a ficha técnica e o simulador em painéis visualmente distintos, mantendo todas as informações e ações existentes.

#### Scenario: Visitante abre um veículo
- **WHEN** o visitante abre a página de um veículo Disponível
- **THEN** a foto, o preço, a ficha técnica e o simulador aparecem com o novo acabamento e continuam funcionando

### Requirement: Home inalterada e comportamento preservado
As mudanças visuais MUST NOT alterar a página inicial nem o comportamento de pesquisa, filtros, página do veículo e simulador, e SHALL funcionar em telas de computador e celular sem rolagem horizontal, respeitando a preferência por movimento reduzido.

#### Scenario: Movimento reduzido nas páginas internas
- **WHEN** o visitante com movimento reduzido abre uma página interna
- **THEN** o banner e as seções aparecem diretamente em seu estado final
