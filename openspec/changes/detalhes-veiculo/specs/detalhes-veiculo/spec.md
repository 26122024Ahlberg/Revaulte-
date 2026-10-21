# Spec Delta

## Purpose

Permite que qualquer visitante consulte, em uma página própria identificada pelo veículo, as informações completas de um veículo publicado, incluindo configuração original e modificações quando cadastradas.

## ADDED Requirements

### Requirement: Página pública do veículo
O sistema SHALL disponibilizar, sem cadastro nem login, uma página para cada veículo Disponível ou Vendido, identificada pelo identificador do veículo, exibindo foto principal, marca, modelo, versão (quando houver), ano, quilometragem em km, condição (Novo ou Usado) e preço em reais, com os mesmos dados mantidos no backend.

#### Scenario: Visitante abre a página de um veículo disponível
- **WHEN** o visitante abre a página de um veículo Disponível
- **THEN** a página exibe foto, título, ano, quilometragem, condição e preço desse veículo

#### Scenario: Veículo sem foto
- **WHEN** o veículo não tem imagem de capa ou ela falha ao carregar
- **THEN** a página exibe a imagem provisória

### Requirement: Acesso a partir dos cartões
Todo cartão de veículo do catálogo, das páginas de Usados e Modificados e dos destaques da página inicial SHALL levar à página daquele veículo, acionável por mouse, toque e teclado.

#### Scenario: Visitante aciona um cartão
- **WHEN** o visitante aciona o cartão de um veículo no estoque
- **THEN** a página daquele veículo é aberta

### Requirement: Configuração original e descrição
A página SHALL exibir cor, motorização, câmbio e descrição do veículo quando estiverem cadastrados, MUST NOT exibir rótulos vazios ou marcadores para dados ausentes e SHALL apresentá-los separados das modificações.

#### Scenario: Dados técnicos parciais
- **WHEN** um veículo tem cor e câmbio cadastrados, mas não motorização
- **THEN** a página exibe cor e câmbio e não exibe o item motorização

### Requirement: Modificações do veículo
Para um veículo indicado como modificado, a página SHALL exibir o selo “Modificado” e a lista de modificações cadastradas, cada uma com sua área e descrição. Quando não houver modificações cadastradas, SHALL informar que os detalhes das modificações não foram informados. A página MUST NOT afirmar ou sugerir que as modificações são legalizadas, homologadas ou regularizadas.

#### Scenario: Veículo modificado com modificações cadastradas
- **WHEN** um veículo modificado com modificações de motor e suspensão cadastradas é aberto
- **THEN** a página lista essas modificações com suas áreas e descrições

#### Scenario: Veículo modificado sem detalhes
- **WHEN** um veículo modificado sem modificações cadastradas é aberto
- **THEN** a página informa que os detalhes das modificações não foram informados

#### Scenario: Veículo original
- **WHEN** um veículo não indicado como modificado é aberto
- **THEN** a página não exibe o selo “Modificado” nem a seção de modificações

### Requirement: Veículo vendido na página de detalhes
Um veículo Vendido SHALL exibir o selo “Vendido” e ser apresentado como indisponível para negociação, sem botão de interesse.

#### Scenario: Visitante abre um veículo vendido
- **WHEN** o visitante abre a página de um veículo Vendido
- **THEN** a página exibe o selo “Vendido”, informa que o veículo está indisponível para negociação e não exibe o botão de interesse

### Requirement: Interesse demonstrativo
Para um veículo Disponível, a página SHALL exibir o botão “Tenho interesse”, que ao ser acionado SHALL apenas informar que o contato com o anunciante ainda não está disponível nesta versão. O botão MUST NOT simular compra, reserva ou envio de mensagem, e a página MUST NOT exibir telefone, e-mail ou endereço do anunciante.

#### Scenario: Visitante aciona “Tenho interesse”
- **WHEN** o visitante aciona “Tenho interesse” em um veículo Disponível
- **THEN** a página informa que o contato com o anunciante ainda não está disponível, sem registrar nenhuma ação

### Requirement: Retorno ao estoque
A página SHALL oferecer a ação “Voltar ao estoque”, que leva a `/estoque`.

#### Scenario: Visitante volta ao estoque
- **WHEN** o visitante aciona “Voltar ao estoque”
- **THEN** a página `/estoque` é aberta

### Requirement: Veículo não encontrado
Quando o identificador não corresponde a um veículo Disponível ou Vendido, incluindo identificador inexistente, não numérico ou de veículo em Rascunho, a página SHALL informar que o veículo não foi encontrado e oferecer o retorno ao estoque. Dados de veículos em Rascunho MUST NOT chegar ao navegador.

#### Scenario: Identificador inexistente
- **WHEN** o visitante abre a página de um identificador que não existe
- **THEN** a página informa que o veículo não foi encontrado e oferece o retorno ao estoque

#### Scenario: Identificador inválido
- **WHEN** o visitante abre `/veiculo/abc`
- **THEN** a página informa que o veículo não foi encontrado

#### Scenario: Veículo em Rascunho
- **WHEN** o visitante abre a página do identificador de um veículo em Rascunho
- **THEN** a página informa que o veículo não foi encontrado e nenhum dado desse veículo é enviado ao navegador

### Requirement: Falha ao obter o veículo
Quando a solicitação ao backend falha, a página SHALL exibir uma mensagem de erro com a opção de tentar novamente, distinta da mensagem de veículo não encontrado, e MUST NOT exibir dados fictícios.

#### Scenario: Backend indisponível
- **WHEN** a solicitação ao backend falha ao abrir a página de um veículo
- **THEN** a página exibe a mensagem de erro e a opção de tentar novamente

### Requirement: Endpoint público de detalhe
O backend SHALL oferecer, sem autenticação, a consulta de um veículo pelo identificador, devolvendo somente veículos Disponíveis ou Vendidos, com os dados de catálogo, cor, motorização, câmbio, descrição e a lista de modificações (área e descrição), e SHALL responder como não encontrado para qualquer outro caso, sem revelar se o veículo existe em Rascunho.

#### Scenario: Consulta de veículo publicado
- **WHEN** o detalhe de um veículo Disponível é solicitado sem token
- **THEN** o backend responde com sucesso e devolve somente os campos previstos e suas modificações

#### Scenario: Consulta de veículo em Rascunho ou inexistente
- **WHEN** o detalhe de um veículo em Rascunho, ou de um identificador inexistente, é solicitado
- **THEN** o backend responde como não encontrado, da mesma forma nos dois casos
