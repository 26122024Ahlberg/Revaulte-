# Spec Delta

## Purpose

Permite que um comprador autenticado converse com o anunciante de um veículo dentro da Revaulte, com histórico associado ao anúncio e acesso restrito aos participantes.

## ADDED Requirements

### Requirement: Iniciar conversa a partir do anúncio
A página de um veículo Disponível SHALL oferecer a ação “Enviar mensagem” ao visitante. Visitante sem sessão SHALL ser levado ao login antes de enviar. Cada par comprador e anúncio SHALL ter uma única conversa, retomada se já existir. O anunciante MUST NOT iniciar conversa consigo mesmo, e veículo Vendido MUST NOT aceitar novas conversas.

#### Scenario: Comprador inicia conversa
- **WHEN** um comprador autenticado aciona “Enviar mensagem” em um veículo Disponível e envia um texto
- **THEN** é criada uma conversa associada a esse anúncio, com a mensagem enviada

#### Scenario: Visitante sem login
- **WHEN** um visitante sem sessão aciona “Enviar mensagem”
- **THEN** o site pede login antes de permitir o envio

#### Scenario: Conversa existente
- **WHEN** o comprador aciona “Enviar mensagem” em um anúncio sobre o qual já conversou
- **THEN** a conversa existente é aberta com o histórico

### Requirement: Histórico e mensagens
Cada conversa SHALL exibir o anúncio associado e as mensagens em ordem cronológica, com autor, data e hora. Mensagens SHALL ter conteúdo de texto não vazio, com tamanho máximo definido.

#### Scenario: Participante abre a conversa
- **WHEN** um participante abre a conversa
- **THEN** vê o anúncio associado e todas as mensagens em ordem cronológica

### Requirement: Acesso restrito aos participantes
O backend SHALL permitir ler e enviar mensagens de uma conversa somente ao comprador e ao anunciante dessa conversa, autenticados. Qualquer outra solicitação SHALL ser recusada sem revelar o conteúdo nem a existência da conversa.

#### Scenario: Terceiro tenta acessar
- **WHEN** um usuário autenticado que não participa da conversa solicita suas mensagens
- **THEN** o backend recusa a solicitação e nenhuma mensagem é devolvida

### Requirement: Não lidas e notificações no site
O site SHALL indicar ao usuário autenticado a quantidade de conversas com mensagens não lidas e SHALL marcar as mensagens como lidas quando o destinatário abrir a conversa.

#### Scenario: Nova mensagem recebida
- **WHEN** o anunciante recebe uma mensagem em uma conversa
- **THEN** o menu da conta indica conversa não lida até ele abri-la
