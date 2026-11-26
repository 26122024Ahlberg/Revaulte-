# Spec Delta

## Purpose

Permite que o Cliente autenticado guarde os veículos públicos de interesse, vinculados à própria conta, consulte-os em uma página própria e remova-os, sem que outra conta tenha acesso à sua lista.

## ADDED Requirements

### Requirement: Favoritar veículo
O Cliente autenticado SHALL poder favoritar e remover dos favoritos um veículo público (Disponível ou Vendido) na página do veículo. A conta MUST ser definida pelo backend a partir do token. Favoritar duas vezes MUST NOT duplicar o favorito.

#### Scenario: Favoritar
- **WHEN** um Cliente autenticado aciona “Favoritar” na página de um veículo
- **THEN** o favorito é gravado, o botão passa a “Remover dos favoritos” e `/favoritos` lista o veículo

#### Scenario: Remover
- **WHEN** o Cliente aciona “Remover dos favoritos”
- **THEN** o favorito é removido e o botão volta a “Favoritar”

#### Scenario: Visitante tenta favoritar
- **WHEN** um visitante sem sessão aciona “Favoritar”
- **THEN** ele é levado a `/entrar?proximo=/veiculo/<id>` e nenhum favorito é gravado

#### Scenario: Favoritar duas vezes
- **WHEN** `POST /favoritos/{id}` é enviado duas vezes pela mesma conta
- **THEN** existe um único favorito e as duas respostas são 200

#### Scenario: Veículo não público
- **WHEN** `POST /favoritos/{id}` é enviado para um Rascunho ou identificador inexistente
- **THEN** a resposta é 404, idêntica nos dois casos, e nada é gravado

### Requirement: Lista de favoritos
A página `/favoritos` SHALL exigir sessão e exibir somente os veículos públicos favoritados pela própria conta, com o cartão do catálogo e a ação “Remover dos favoritos”. Favoritos de outra conta MUST NOT ser visíveis. Veículo Vendido SHALL continuar na lista com o selo “Vendido”; veículo que deixou de ser público SHALL deixar de aparecer.

#### Scenario: Lista com itens
- **WHEN** um Cliente com favoritos abre `/favoritos`
- **THEN** vê os cartões dos seus favoritos, do mais recente ao mais antigo

#### Scenario: Lista vazia
- **WHEN** um Cliente sem favoritos abre `/favoritos`
- **THEN** vê “Você ainda não favoritou nenhum veículo” e um link para o Estoque

#### Scenario: Visitante
- **WHEN** um visitante abre `/favoritos`
- **THEN** é levado a `/entrar?proximo=/favoritos`

#### Scenario: Erro
- **WHEN** a consulta falha
- **THEN** a página mostra mensagem genérica e “Tentar novamente”, sem texto cru do backend

### Requirement: Autorização dos endpoints de favoritos
Todos os endpoints do grupo `Favoritos` SHALL exigir token (401 sem ele) e cargo (403 sem cargo), e MUST NOT aceitar identificador de conta na entrada.

#### Scenario: Sem token
- **WHEN** qualquer endpoint de favoritos é chamado sem token
- **THEN** a resposta é 401

#### Scenario: Isolamento
- **WHEN** a conta B consulta `GET /favoritos`
- **THEN** a resposta não contém favoritos da conta A
