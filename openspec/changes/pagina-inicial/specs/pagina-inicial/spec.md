# Spec Delta

## Purpose

Apresenta a Revaulte ao visitante na raiz do site, comunicando a especialidade da loja e levando aos veículos reais do estoque, com uma seleção de destaques vinda do backend.

## ADDED Requirements

### Requirement: Página inicial pública na raiz
O sistema SHALL exibir a página inicial da Revaulte no endereço `/`, sem exigir cadastro ou login, com o menu principal e o item Home identificado como página atual.

#### Scenario: Visitante abre a raiz
- **WHEN** um visitante sem sessão abre `/`
- **THEN** a página inicial é exibida, sem redirecionamento para outra página

### Requirement: Banner principal em carrossel
A página inicial SHALL exibir um banner em carrossel com três slides, nesta ordem: esportivo, modificado e clássico. Cada slide SHALL ter uma fotografia horizontal com texto alternativo, a categoria, uma frase de impacto e o botão “Explorar estoque”, que leva a `/estoque`. Somente um slide SHALL ficar visível por vez; o primeiro é exibido ao abrir a página. O visitante SHALL poder trocar de slide por setas “anterior” e “próximo” e por indicadores de posição, todos acionáveis por mouse, toque e teclado e identificados para tecnologias assistivas. A troca MUST NOT ocorrer automaticamente. Os slides ocultos MUST NOT receber foco do teclado. O texto do slide SHALL continuar legível se a fotografia não carregar.

#### Scenario: Visitante avança e volta
- **WHEN** o visitante aciona a seta “próximo” no primeiro slide
- **THEN** o slide do modificado é exibido e o indicador de posição passa ao segundo slide

#### Scenario: Navegação circular
- **WHEN** o visitante aciona “próximo” no último slide, ou “anterior” no primeiro
- **THEN** o carrossel passa, respectivamente, ao primeiro ou ao último slide

#### Scenario: Indicador de posição
- **WHEN** o visitante aciona o indicador do terceiro slide
- **THEN** o slide do clássico é exibido

#### Scenario: Visitante explora o estoque
- **WHEN** o visitante aciona “Explorar estoque” em qualquer slide
- **THEN** a página `/estoque` é aberta

#### Scenario: Imagem do slide indisponível
- **WHEN** a fotografia do slide exibido não carrega
- **THEN** a frase de impacto e o botão continuam visíveis e legíveis sobre o fundo escuro

### Requirement: Veículos em destaque
A página inicial SHALL exibir, na seção “Veículos em destaque”, os três veículos no estado Disponível cadastrados mais recentemente, obtidos do backend no carregamento da página e apresentados com as mesmas informações e selos dos cartões do catálogo. Veículos Vendidos MUST NOT aparecer nos destaques. A seção SHALL oferecer um link para o estoque completo.

#### Scenario: Mais de três disponíveis
- **WHEN** existem cinco veículos Disponíveis no backend
- **THEN** a seção exibe somente os três cadastrados mais recentemente, do mais recente para o mais antigo

#### Scenario: Vendido não é destaque
- **WHEN** o veículo cadastrado mais recentemente está no estado Vendido
- **THEN** ele não aparece nos destaques e a seção exibe os três Disponíveis mais recentes

#### Scenario: Menos de três disponíveis
- **WHEN** existem apenas dois veículos Disponíveis
- **THEN** a seção exibe esses dois veículos

#### Scenario: Nenhum disponível
- **WHEN** não há veículos Disponíveis
- **THEN** a seção exibe uma mensagem informando que não há destaques no momento e mantém o link para o estoque

#### Scenario: Falha ao obter os destaques
- **WHEN** a solicitação ao backend falha
- **THEN** a seção exibe uma mensagem de erro com a opção de tentar novamente, não exibe veículos fictícios, e o restante da página continua utilizável

### Requirement: Seção de proposta da Revaulte
A página inicial SHALL apresentar uma seção descrevendo a especialidade da Revaulte em carros antigos, clássicos, esportivos e modificados/preparados. O texto MUST NOT afirmar serviços, garantias, laudos, condições de financiamento ou dados de contato que não estejam definidos na documentação do projeto.

#### Scenario: Visitante lê a proposta
- **WHEN** o visitante percorre a página inicial
- **THEN** encontra a seção que explica a especialidade da Revaulte, sem promessas de serviços não definidos

### Requirement: Animações leves da página inicial
O banner, a troca de slides e as seções da página inicial SHALL usar animações leves e curtas, sem impedir a leitura nem o uso do conteúdo. Quando o visitante indica preferência por movimento reduzido, a página SHALL exibir todo o conteúdo e cada slide diretamente em seu estado final, sem transição.

#### Scenario: Movimento reduzido
- **WHEN** o visitante com a preferência por movimento reduzido ativada abre `/`
- **THEN** o banner e as seções aparecem sem animação de entrada, e a troca de slides acontece sem transição
