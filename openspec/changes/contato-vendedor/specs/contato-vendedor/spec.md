# Spec Delta

## Purpose

Permite que o visitante saiba quem anuncia um veículo e entre em contato com o anunciante por um meio que ele autorizou, sem expor outros dados pessoais.

## ADDED Requirements

### Requirement: Anunciante na página do veículo
A página de um veículo Disponível SHALL exibir o nome de exibição do anunciante vinculado ao anúncio no backend. Os dados do anunciante MUST corresponder ao que está cadastrado e MUST NOT ser fictícios.

#### Scenario: Veículo com anunciante
- **WHEN** o visitante abre a página de um veículo Disponível vinculado a um anunciante
- **THEN** a página exibe o nome de exibição desse anunciante

### Requirement: Contato autorizado pelo WhatsApp
Quando o veículo Disponível tem anunciante real vinculado, com número de WhatsApp válido e autorização explícita para exibi-lo, a página SHALL oferecer, no bloco “Anunciado por”, a ação “Conversar no WhatsApp”, que abre o WhatsApp com o número do anunciante e uma mensagem inicial que identifica o veículo pelo título e pelo ano. Enquanto não houver domínio público, a mensagem MUST NOT incluir endereço do anúncio, e nunca um endereço local (`localhost`). Em qualquer outro caso, a página SHALL exibir “Contato não disponível”. O site MUST NOT enviar mensagens em nome do visitante nem registrar o contato.

#### Scenario: Visitante aciona o contato
- **WHEN** o visitante aciona “Conversar no WhatsApp” em um veículo cujo anunciante autorizou o contato
- **THEN** o WhatsApp é aberto com o número do anunciante e a mensagem inicial com o título e o ano do veículo, sem endereço local

#### Scenario: Contato não autorizado
- **WHEN** o anunciante não autorizou a exibição do contato, ou o veículo não tem anunciante vinculado
- **THEN** a página exibe “Contato não disponível” e não exibe número nem link

#### Scenario: Número inválido
- **WHEN** o número cadastrado não tem somente dígitos, com DDI e DDD (12 ou 13 dígitos)
- **THEN** a página exibe “Contato não disponível” e não exibe link

### Requirement: Veículo vendido sem contato
A página de um veículo Vendido MUST NOT exibir o contato do anunciante.

#### Scenario: Veículo vendido
- **WHEN** o visitante abre a página de um veículo Vendido
- **THEN** a página não exibe número nem a ação de contato

### Requirement: Dados públicos mínimos do anunciante
O backend SHALL expor publicamente, no detalhe de um veículo Disponível, somente o nome de exibição do anunciante e, quando autorizado, o número de contato. O backend MUST NOT expor o identificador interno do anunciante (`seller_id`), a autorização e sua data, e-mail, CPF, endereço, dados de conta ou o contato de anunciantes que não autorizaram; MUST NOT expor o anunciante de veículo Vendido; e a listagem pública do catálogo MUST NOT incluir dados do anunciante.

#### Scenario: Consulta sem autorização de contato
- **WHEN** o detalhe de um veículo cujo anunciante não autorizou o contato é solicitado sem token
- **THEN** a resposta contém o nome de exibição e não contém o número nem o identificador do anunciante

#### Scenario: Consulta de veículo vendido
- **WHEN** o detalhe de um veículo Vendido com anunciante é solicitado
- **THEN** a resposta não contém dados do anunciante

#### Scenario: Listagem pública
- **WHEN** a listagem pública de veículos é solicitada
- **THEN** a resposta não contém número de contato de nenhum anunciante
