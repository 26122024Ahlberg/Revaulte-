# Spec Delta

## Purpose

Permite que o Cliente autenticado envie anúncios de veículos à Revaulte e consulte somente os próprios anúncios, com o vínculo entre conta, anunciante e veículo definido e protegido pelo backend, sem expor rascunhos no catálogo público.

## ADDED Requirements

### Requirement: Páginas de anúncios exigem sessão
As páginas `/anunciar`, `/meus-anuncios` e `/meus-anuncios/<id>` SHALL exigir sessão confirmada no backend. O visitante sem sessão SHALL ser levado a `/entrar` e, após o login, de volta à página pedida.

#### Scenario: Visitante abre Anunciar veículo
- **WHEN** um visitante sem sessão abre `/anunciar`
- **THEN** ele é levado a `/entrar?proximo=/anunciar` e, após entrar, volta para `/anunciar`

#### Scenario: Sessão expirada em Meus anúncios
- **WHEN** um Cliente com token expirado abre `/meus-anuncios`
- **THEN** a sessão é encerrada e ele é levado a `/entrar?proximo=/meus-anuncios`, sem exibir anúncios

### Requirement: Envio de anúncio pelo Cliente
O Cliente autenticado SHALL poder enviar um anúncio informando marca, modelo, ano, condição (novo ou usado), quilometragem, preço e se o veículo é modificado. Versão, cor, motorização, câmbio e descrição SHALL ser opcionais. Após o envio aceito, o Cliente SHALL ser levado a “Meus anúncios”, com o novo anúncio na lista.

#### Scenario: Anúncio válido
- **WHEN** um Cliente preenche os campos obrigatórios com valores válidos e envia o formulário
- **THEN** o anúncio é criado, o Cliente é levado a `/meus-anuncios` e o novo anúncio aparece com o estado Rascunho

#### Scenario: Envio em andamento
- **WHEN** o Cliente aciona o envio
- **THEN** o botão fica desabilitado até a resposta, evitando envios repetidos

### Requirement: Validação dos dados do anúncio
O backend SHALL recusar o anúncio com erro de validação quando um campo obrigatório faltar ou um valor estiver fora dos limites definidos no `design.md` (por exemplo, ano, quilometragem e preço). O frontend SHALL aplicar as mesmas regras antes de enviar e exibir a mensagem do primeiro problema, sem perder os dados digitados.

#### Scenario: Campo obrigatório ausente
- **WHEN** o Cliente envia o formulário sem a marca
- **THEN** o anúncio não é criado e a página informa que a marca é obrigatória

#### Scenario: Valor fora do limite no backend
- **WHEN** uma requisição autenticada chega ao backend com preço zero ou negativo
- **THEN** o backend responde com erro de validação e nenhum registro é criado

### Requirement: Anúncio nasce como Rascunho
Todo anúncio criado pelo site SHALL ser gravado no estado Rascunho, independentemente do que a requisição enviar. Somente a equipe SHALL publicá-lo, fora do site.

#### Scenario: Tentativa de publicar diretamente
- **WHEN** uma requisição autenticada de criação inclui `status` igual a `available`
- **THEN** o anúncio é criado em Rascunho

#### Scenario: Rascunho fora do catálogo público
- **WHEN** um anúncio de Cliente em Rascunho existe e o catálogo, os destaques e o detalhe público são consultados sem token
- **THEN** o anúncio não aparece na listagem nem nos destaques, e o detalhe público responde como inexistente (404)

### Requirement: Vínculo definido pela sessão
O backend SHALL associar o anúncio ao anunciante da conta autenticada, criando esse anunciante no primeiro anúncio. Cada conta SHALL ter no máximo um anunciante. Identificadores de conta, anunciante, estado, imagem ou data enviados na requisição MUST NOT ser aceitos.

#### Scenario: Primeiro anúncio da conta
- **WHEN** um Cliente sem anunciante cria seu primeiro anúncio
- **THEN** um anunciante ligado à conta é criado e o anúncio é associado a ele

#### Scenario: Segundo anúncio da conta
- **WHEN** o mesmo Cliente cria outro anúncio
- **THEN** o anúncio é associado ao mesmo anunciante, sem criar outro

#### Scenario: Tentativa de anunciar em nome de outro
- **WHEN** uma requisição autenticada de criação inclui `seller_id`, `user_id` ou `id` de outra conta ou anunciante
- **THEN** esses valores são ignorados e o anúncio fica associado somente ao anunciante da conta do token

#### Scenario: Envios simultâneos do primeiro anúncio
- **WHEN** duas requisições de criação da mesma conta, ainda sem anunciante, chegam ao mesmo tempo
- **THEN** a conta fica com um único anunciante; cada requisição ou é aceita com o anúncio ligado a ele, ou é recusada sem gravar anúncio nem anunciante, e nenhum registro é apagado

### Requirement: Limite de rascunhos por conta
Uma criação recebida quando a conta já tem 20 anúncios em Rascunho SHALL ser recusada sem gravar nada, e a página SHALL informar que é preciso aguardar a publicação de anúncios pendentes. Anúncios publicados ou vendidos MUST NOT contar para o limite.

#### Scenario: Vigésimo primeiro rascunho
- **WHEN** um Cliente com 20 anúncios em Rascunho envia outro anúncio válido
- **THEN** o backend recusa com o código `draft_limit_reached`, nenhum registro é criado e a página explica o limite

#### Scenario: Rascunho publicado libera vaga
- **WHEN** a equipe publica um dos 20 rascunhos de um Cliente e ele envia outro anúncio
- **THEN** o novo anúncio é criado em Rascunho

### Requirement: Nome de exibição do anunciante
No primeiro anúncio, o Cliente SHALL informar o nome de exibição do anunciante, preenchido inicialmente com o nome da conta e editável. Nos anúncios seguintes, o nome definido SHALL ser mantido e exibido sem edição. O nome de exibição SHALL ser o único dado do anunciante exibido publicamente.

#### Scenario: Primeiro anúncio com nome próprio
- **WHEN** no primeiro anúncio o Cliente troca o nome sugerido por “Garagem Exemplo”
- **THEN** o anunciante é criado com o nome de exibição “Garagem Exemplo”

#### Scenario: Anúncios seguintes
- **WHEN** um Cliente que já tem anunciante abre `/anunciar`
- **THEN** o formulário mostra o nome de exibição atual sem permitir alterá-lo, e um nome enviado na requisição é ignorado

### Requirement: Contato não autorizado por padrão
O anunciante criado pelo site SHALL ser gravado sem número de contato e sem autorização de exibição. A página pública de um anúncio de Cliente publicado MUST NOT exibir número de contato.

#### Scenario: Anúncio de Cliente publicado pela equipe
- **WHEN** a equipe publica um anúncio de Cliente e um visitante abre a página do veículo
- **THEN** a página exibe o nome de exibição do anunciante e informa que o contato não está disponível, sem número de WhatsApp

### Requirement: Consulta dos próprios anúncios
“Meus anúncios” SHALL listar somente os anúncios do anunciante da conta autenticada, do mais recente para o mais antigo, com título, ano, preço e estado (“Rascunho — aguardando publicação”, “Publicado” ou “Vendido”). Conta sem anúncios SHALL ver uma mensagem e o link para anunciar.

#### Scenario: Cliente com anúncios
- **WHEN** um Cliente com dois anúncios abre `/meus-anuncios`
- **THEN** a página lista os dois, com o estado de cada um, e nenhum anúncio de outra conta

#### Scenario: Cliente sem anúncios
- **WHEN** um Cliente sem anúncios abre `/meus-anuncios`
- **THEN** a página informa que ainda não há anúncios e oferece o link “Anunciar veículo”

#### Scenario: Falha ao carregar
- **WHEN** o backend não responde ou responde com erro inesperado
- **THEN** a página exibe uma mensagem de erro com a opção de tentar novamente, sem lista parcial

### Requirement: Ficha privada do próprio anúncio
A página `/meus-anuncios/<id>` SHALL mostrar ao dono a ficha completa do anúncio, inclusive em Rascunho, e o estado atual. Anúncio publicado SHALL oferecer o link para a página pública. A página MUST NOT oferecer edição nem exclusão.

#### Scenario: Dono abre um Rascunho
- **WHEN** o dono abre `/meus-anuncios/<id>` de um anúncio em Rascunho
- **THEN** a página mostra os dados enviados e o estado “Rascunho — aguardando publicação”, sem link para a página pública

#### Scenario: Identificador inválido
- **WHEN** o Cliente abre `/meus-anuncios/abc`
- **THEN** a página informa que o anúncio não foi encontrado, sem consultar o backend

### Requirement: Autorização sobre anúncios no backend
Os endpoints de anúncios SHALL exigir token válido de conta existente com perfil Cliente ou Administrador. Um anúncio de outra conta, um anúncio sem anunciante ligado a conta e um identificador inexistente SHALL receber a mesma resposta 404, sem revelar dados. Nenhum endpoint desta capacidade SHALL alterar ou excluir anúncios existentes.

#### Scenario: Sem token
- **WHEN** qualquer endpoint de anúncios é chamado sem token ou com token inválido
- **THEN** a resposta é 401 e nenhum dado de anúncio é devolvido

#### Scenario: Anúncio de outra conta
- **WHEN** o Cliente B solicita a ficha privada de um anúncio do Cliente A
- **THEN** a resposta é 404, igual à de um identificador inexistente

#### Scenario: Veículo cadastrado pela equipe
- **WHEN** um Cliente solicita a ficha privada de um dos veículos cadastrados pela equipe (por exemplo, o Opala)
- **THEN** a resposta é 404 e o veículo não aparece em nenhuma lista de “Meus anúncios”

#### Scenario: Conta sem cargo
- **WHEN** uma conta com perfil nulo chama um endpoint de anúncios
- **THEN** a resposta é 403 e nenhum dado é devolvido

### Requirement: Respostas privadas sem dados internos
As respostas dos endpoints de anúncios MUST NOT conter dados pessoais da conta (CPF, telefone, data de nascimento, endereço, e-mail, senha), identificadores de conta ou de anunciante, número de contato nem autorização de contato.

#### Scenario: Lista sem dados pessoais
- **WHEN** o Cliente obtém a lista dos próprios anúncios
- **THEN** cada item contém somente os campos do anúncio previstos no `design.md`, e a resposta não contém `user_id`, `seller_id`, `whatsapp` nem dados cadastrais

### Requirement: Limite de requisições
Quando o backend recusar a requisição por excesso de requisições (429), as páginas de anúncios SHALL informar que há muitas tentativas e pedir que o Cliente aguarde um pouco antes de tentar novamente, sem perder os dados do formulário.

#### Scenario: Envio recusado por limite
- **WHEN** o envio do formulário recebe 429
- **THEN** a página pede que o Cliente aguarde e tente novamente, e os campos continuam preenchidos

### Requirement: Preservação dos dados existentes
A implantação desta capacidade MUST NOT alterar os veículos, as modificações, as contas, os anunciantes nem o vínculo e a autorização de contato existentes. O catálogo público SHALL continuar com o mesmo conteúdo enquanto a equipe não publicar novos anúncios.

#### Scenario: Catálogo após a implantação
- **WHEN** o catálogo público é consultado logo após a implantação
- **THEN** ele contém os mesmos veículos de antes, com os mesmos dados

#### Scenario: Contato do Opala após a implantação
- **WHEN** o detalhe público do Opala é consultado após a implantação
- **THEN** o anunciante e o contato autorizado são exibidos como antes
