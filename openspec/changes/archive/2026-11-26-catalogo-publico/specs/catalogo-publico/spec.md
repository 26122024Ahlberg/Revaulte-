# Spec Delta

## Purpose

Permite que qualquer visitante consulte, em uma página própria e sem autenticação, a listagem dos veículos publicados pela loja, com informações resumidas e a identificação de veículos modificados e vendidos.

## ADDED Requirements

### Requirement: Página própria de catálogo com acesso público
O sistema SHALL disponibilizar o catálogo de veículos em uma página própria, acessível sem cadastro e sem login.

#### Scenario: Visitante acessa o catálogo sem sessão
- **WHEN** um visitante sem sessão autenticada abre a página do catálogo
- **THEN** a listagem de veículos é exibida sem solicitação de login ou cadastro

#### Scenario: Listagem pública consultada sem credenciais
- **WHEN** a listagem pública de veículos é solicitada ao backend sem nenhum token de autenticação
- **THEN** o backend responde com sucesso e devolve a listagem

### Requirement: Veículos exibidos provêm do backend
A página do catálogo SHALL exibir exclusivamente os veículos devolvidos pelo backend no momento do carregamento, sem veículos fixos no código da página.

#### Scenario: Veículo publicado aparece no catálogo
- **WHEN** existe no backend um veículo no estado Disponível e a página do catálogo é carregada
- **THEN** esse veículo aparece na listagem com os dados mantidos no backend

#### Scenario: Alteração no backend é refletida
- **WHEN** o preço de um veículo publicado é alterado no backend e a página do catálogo é recarregada
- **THEN** a listagem exibe o novo preço

### Requirement: Somente veículos Disponíveis e Vendidos são públicos
A listagem pública SHALL conter somente veículos nos estados Disponível e Vendido. Veículos em Rascunho MUST NOT ser devolvidos pelo backend na listagem pública, de modo que seus dados nunca cheguem ao navegador.

#### Scenario: Veículo em Rascunho não é devolvido
- **WHEN** existe um veículo em Rascunho e a listagem pública é solicitada ao backend
- **THEN** a resposta não contém esse veículo nem qualquer dado dele

#### Scenario: Veículo em Rascunho não aparece na página
- **WHEN** existem veículos em Rascunho, Disponível e Vendido e a página do catálogo é carregada
- **THEN** somente os veículos Disponível e Vendido aparecem na listagem

#### Scenario: Existem apenas veículos em Rascunho
- **WHEN** todos os veículos cadastrados estão em Rascunho e a página do catálogo é carregada
- **THEN** a página exibe a mensagem de catálogo vazio

### Requirement: Resposta pública limitada aos dados do catálogo
A listagem pública SHALL devolver, para cada veículo, somente os dados necessários à exibição no catálogo: identificador, marca, modelo, versão, ano, condição, quilometragem, preço, indicação de veículo modificado, estado e imagem de capa.

#### Scenario: Resposta não expõe outros dados
- **WHEN** a listagem pública é solicitada ao backend
- **THEN** cada veículo da resposta contém apenas os dados de catálogo previstos, sem outros campos do registro

### Requirement: Informações resumidas de cada veículo
A página do catálogo SHALL exibir, para cada veículo listado, marca, modelo, ano, quilometragem, preço e condição (Novo ou Usado). A versão SHALL ser exibida quando estiver cadastrada. O preço SHALL ser apresentado em reais e a quilometragem em quilômetros.

#### Scenario: Veículo usado com todos os dados
- **WHEN** um veículo usado, de marca Chevrolet, modelo Opala, versão SS, ano 1978, com 72000 km e preço 118900 é listado
- **THEN** seu cartão exibe marca, modelo e versão, o ano 1978, a quilometragem em km, o preço em reais e a condição “Usado”

#### Scenario: Veículo novo
- **WHEN** um veículo cadastrado com a condição novo é listado
- **THEN** seu cartão exibe a condição “Novo”

#### Scenario: Veículo sem versão cadastrada
- **WHEN** um veículo sem versão cadastrada é listado
- **THEN** seu cartão exibe marca e modelo sem texto vazio ou marcador no lugar da versão

### Requirement: Identificação de veículos modificados
A página do catálogo SHALL identificar visualmente, com o selo “Modificado”, todo veículo indicado como modificado/preparado. Veículos originais MUST NOT exibir esse selo. A identificação SHALL ser independente da condição (novo ou usado) e do estado do veículo.

#### Scenario: Veículo modificado
- **WHEN** um veículo indicado como modificado é listado
- **THEN** seu cartão exibe o selo “Modificado”

#### Scenario: Veículo original
- **WHEN** um veículo não indicado como modificado é listado
- **THEN** seu cartão não exibe o selo “Modificado”

#### Scenario: Veículo novo e modificado
- **WHEN** um veículo com a condição novo e indicado como modificado é listado
- **THEN** seu cartão exibe a condição “Novo” e o selo “Modificado”

### Requirement: Identificação de veículos vendidos
A página do catálogo SHALL identificar visualmente, com o selo “Vendido”, todo veículo no estado Vendido, e SHALL apresentá-lo como indisponível para negociação, com aparência distinta dos veículos disponíveis. Veículos no estado Disponível MUST NOT exibir o selo “Vendido”. A identificação SHALL ser perceptível pelo texto do selo, e não apenas por cor.

#### Scenario: Veículo vendido
- **WHEN** um veículo no estado Vendido é listado
- **THEN** seu cartão exibe o selo “Vendido” e aparência distinta da dos veículos disponíveis

#### Scenario: Veículo disponível
- **WHEN** um veículo no estado Disponível é listado
- **THEN** seu cartão não exibe o selo “Vendido”

#### Scenario: Veículo vendido e modificado
- **WHEN** um veículo no estado Vendido e indicado como modificado é listado
- **THEN** seu cartão exibe os selos “Vendido” e “Modificado”

### Requirement: Imagem do veículo no catálogo
A página do catálogo SHALL exibir a imagem de capa do veículo quando houver uma cadastrada e SHALL exibir uma imagem provisória quando não houver ou quando a imagem não puder ser carregada.

#### Scenario: Veículo com imagem de capa
- **WHEN** um veículo com imagem de capa cadastrada é listado
- **THEN** seu cartão exibe essa imagem com texto alternativo que identifica o veículo

#### Scenario: Veículo sem imagem de capa
- **WHEN** um veículo sem imagem de capa cadastrada é listado
- **THEN** seu cartão exibe a imagem provisória

#### Scenario: Imagem de capa indisponível
- **WHEN** a imagem de capa de um veículo listado falha ao carregar
- **THEN** seu cartão exibe a imagem provisória no lugar

### Requirement: Estados de carregamento, vazio e erro
A página do catálogo SHALL informar o visitante enquanto a listagem é carregada, quando não há veículos a exibir e quando a listagem não pôde ser obtida. Em caso de falha, a página MUST NOT exibir veículos fictícios e SHALL oferecer uma forma de tentar novamente.

#### Scenario: Listagem em carregamento
- **WHEN** a página do catálogo foi aberta e a resposta do backend ainda não chegou
- **THEN** a página exibe uma indicação de carregamento

#### Scenario: Catálogo vazio
- **WHEN** o backend devolve uma listagem sem veículos
- **THEN** a página exibe uma mensagem informando que não há veículos no catálogo

#### Scenario: Falha ao obter a listagem
- **WHEN** a solicitação ao backend falha ou devolve erro
- **THEN** a página exibe uma mensagem de erro, não exibe nenhum veículo e oferece uma ação para tentar novamente

#### Scenario: Nova tentativa bem-sucedida
- **WHEN** o visitante aciona a ação de tentar novamente e o backend responde com sucesso
- **THEN** a mensagem de erro é substituída pela listagem de veículos
