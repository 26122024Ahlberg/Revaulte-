# Spec Delta

## Purpose

Permite que o visitante encontre veículos no estoque da Revaulte pesquisando por marca, modelo e versão e filtrando por condição e por modificação.

## ADDED Requirements

### Requirement: Pesquisa por texto
As páginas de estoque (`/estoque`, `/usados` e `/modificados`) SHALL oferecer um campo de pesquisa que restringe a listagem aos veículos cuja marca, modelo ou versão contenha o texto informado, sem diferenciar maiúsculas, minúsculas e acentos e ignorando espaços nas extremidades. Com o campo vazio, nenhum veículo é excluído pela pesquisa.

#### Scenario: Pesquisa por modelo
- **WHEN** o visitante pesquisa “opala” e o estoque contém um Chevrolet Opala SS
- **THEN** o Chevrolet Opala SS aparece e os veículos sem “opala” na marca, no modelo ou na versão não aparecem

#### Scenario: Pesquisa sem acento
- **WHEN** o visitante pesquisa “citroen” e o estoque contém um veículo da marca Citroën
- **THEN** esse veículo aparece no resultado

#### Scenario: Pesquisa vazia
- **WHEN** o campo de pesquisa está vazio ou contém apenas espaços
- **THEN** a listagem exibe todos os veículos da página, sujeitos apenas aos filtros

### Requirement: Filtros por condição e modificação
A página `/estoque` SHALL oferecer os filtros de condição (Todos, Novo, Usado) e de modificação (Todos, Modificados, Originais). A página `/usados` SHALL oferecer somente o filtro de modificação, e a página `/modificados` somente o filtro de condição, preservando o recorte fixo de cada página. Os filtros e a pesquisa SHALL ser combinados: um veículo só aparece se atender a todos.

#### Scenario: Usados modificados
- **WHEN** o visitante seleciona condição Usado e modificação Modificados em `/estoque`
- **THEN** somente veículos usados e modificados aparecem

#### Scenario: Pesquisa combinada com recorte
- **WHEN** o visitante pesquisa “gol” em `/modificados`
- **THEN** somente veículos modificados que contenham “gol” na marca, no modelo ou na versão aparecem

#### Scenario: Vendidos continuam filtráveis
- **WHEN** um veículo Vendido atende à pesquisa e aos filtros
- **THEN** ele aparece com o selo “Vendido”

### Requirement: Nenhum resultado
Quando a pesquisa e os filtros não retornam veículos, a página SHALL informar que nenhum veículo corresponde aos critérios e SHALL oferecer a ação “Limpar filtros”, que restaura a pesquisa vazia e os filtros em Todos. Essa mensagem SHALL ser distinta da mensagem de catálogo vazio.

#### Scenario: Pesquisa sem resultado
- **WHEN** o visitante pesquisa um texto que nenhum veículo contém
- **THEN** a página informa que nenhum veículo corresponde aos critérios e exibe “Limpar filtros”

#### Scenario: Limpar filtros
- **WHEN** o visitante aciona “Limpar filtros”
- **THEN** o campo de pesquisa fica vazio, os filtros voltam a Todos e a listagem completa da página é exibida

### Requirement: Filtragem sem nova consulta ao backend
A pesquisa e os filtros SHALL ser aplicados sobre a listagem pública já obtida no carregamento da página, sem alterar as regras de visibilidade do backend.

#### Scenario: Alteração de filtro
- **WHEN** o visitante altera a pesquisa ou um filtro
- **THEN** a listagem é atualizada sem nova solicitação ao backend e sem exibir veículos em Rascunho
