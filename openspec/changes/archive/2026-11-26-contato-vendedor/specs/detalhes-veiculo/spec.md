# Spec Delta

## MODIFIED Requirements

### Requirement: Veículo vendido na página de detalhes
Um veículo Vendido SHALL exibir o selo “Vendido” e ser apresentado como indisponível para negociação, sem ação de contato.

#### Scenario: Visitante abre um veículo vendido
- **WHEN** o visitante abre a página de um veículo Vendido
- **THEN** a página exibe o selo “Vendido”, informa que o veículo está indisponível para negociação e não exibe ação de contato

### Requirement: Endpoint público de detalhe
O backend SHALL oferecer, sem autenticação, a consulta de um veículo pelo identificador, devolvendo somente veículos Disponíveis ou Vendidos, com os dados de catálogo, cor, motorização, câmbio, descrição, a lista de modificações (área e descrição) e os dados públicos do anunciante permitidos pela capability `contato-vendedor`, e SHALL responder como não encontrado para qualquer outro caso, sem revelar se o veículo existe em Rascunho.

#### Scenario: Consulta de veículo publicado
- **WHEN** o detalhe de um veículo Disponível é solicitado sem token
- **THEN** o backend responde com sucesso e devolve somente os campos previstos, suas modificações e os dados públicos permitidos do anunciante

#### Scenario: Consulta de veículo em Rascunho ou inexistente
- **WHEN** o detalhe de um veículo em Rascunho, ou de um identificador inexistente, é solicitado
- **THEN** o backend responde como não encontrado, da mesma forma nos dois casos

## REMOVED Requirements

### Requirement: Interesse demonstrativo

**Reason**: Decisão do usuário em 07/11/2026: o botão demonstrativo “Tenho interesse” foi substituído pelo bloco do anunciante com contato pelo WhatsApp.

**Migration**: O contato é descrito pela capability `contato-vendedor`.
