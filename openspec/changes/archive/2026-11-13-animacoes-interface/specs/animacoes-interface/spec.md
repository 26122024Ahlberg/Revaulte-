# Spec Delta

## Purpose

Define como a interface pública da Revaulte usa movimento: transições discretas que reforçam a identidade sem prejudicar acessibilidade, desempenho ou leitura do conteúdo.

## ADDED Requirements

### Requirement: Movimento reduzido
Quando o visitante indica no sistema a preferência por movimento reduzido, a interface SHALL exibir todo o conteúdo em seu estado final, sem animações de entrada, deslocamento ou rotação.

#### Scenario: Preferência por movimento reduzido
- **WHEN** o visitante com movimento reduzido ativado abre qualquer página
- **THEN** seções, cartões e indicações de carregamento aparecem sem animação

### Requirement: Conteúdo independente da animação
Nenhum conteúdo SHALL depender da conclusão de uma animação para ficar visível ou acionável, e as animações MUST NOT provocar rolagem horizontal nem deslocar o layout já exibido.

#### Scenario: Cartões aparecem com animação
- **WHEN** a listagem de veículos é exibida
- **THEN** os cartões ficam visíveis e acionáveis ao fim de uma transição de até 0,5 s, sem rolagem horizontal

### Requirement: Foco visível
Cartões, botões, links do menu e controles de pesquisa SHALL exibir indicação de foco visível ao serem alcançados pelo teclado, com contraste perceptível sobre o fundo escuro.

#### Scenario: Navegação por teclado
- **WHEN** o visitante percorre a página com a tecla Tab
- **THEN** cada elemento acionável alcançado exibe indicação de foco visível

### Requirement: Carregamento perceptível e acessível
Os estados de carregamento SHALL exibir uma indicação animada acompanhada de texto disponível a tecnologias assistivas.

#### Scenario: Catálogo carregando
- **WHEN** a listagem ainda está sendo obtida
- **THEN** a página exibe a indicação animada e o texto de carregamento é anunciado por leitores de tela
