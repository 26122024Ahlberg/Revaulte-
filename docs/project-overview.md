# GhostPay — Visão Geral do Projeto

## 1. Visão geral

O GhostPay é uma plataforma web voltada à divulgação de veículos para venda.

A plataforma permitirá que visitantes naveguem pelo catálogo de veículos disponíveis sem a necessidade de possuir uma conta. O site apresentará informações sobre os veículos e permitirá que o usuário consulte detalhes de um veículo específico.

Cada anúncio representa um veículo real. O GhostPay poderá anunciar veículos novos e usados, tanto originais quanto modificados/preparados. A apresentação de veículos modificados é um ponto importante do projeto: a plataforma distingue a configuração original do veículo das modificações realizadas posteriormente.

Usuários também poderão criar uma conta e realizar login na plataforma. A conta oferece funcionalidades adicionais, como favoritar veículos e salvar simulações de financiamento.

O GhostPay não realizará a conclusão da compra do veículo diretamente pelo site. A plataforma funcionará como meio de apresentação dos veículos, consulta de sua configuração original e de suas modificações, simulação de financiamento e contato entre o cliente interessado e a loja.

O GhostPay não é um configurador de veículo novo de montadora: o usuário consulta a configuração do veículo anunciado, sem montá-la.

Também existirá uma área administrativa destinada ao gerenciamento dos veículos anunciados na plataforma.

## 2. Problema

A busca e negociação de veículos pode envolver informações distribuídas em diferentes canais, dificultando a consulta das opções disponíveis e o contato entre clientes interessados e a loja.

O GhostPay busca centralizar a apresentação dos veículos em uma plataforma web, permitindo que potenciais clientes consultem o catálogo, analisem informações dos veículos, conheçam a configuração original e as modificações de cada um, realizem simulações de financiamento e entrem em contato com a loja.

## 3. Objetivos

O objetivo principal do GhostPay é disponibilizar uma plataforma web simples para apresentação e divulgação dos veículos oferecidos pela loja.

Entre os objetivos do projeto estão:

- permitir a navegação pública pelo catálogo de veículos;
- anunciar veículos novos e usados, originais ou modificados/preparados;
- apresentar informações detalhadas de cada veículo;
- apresentar a configuração original do veículo e, quando houver, suas modificações;
- permitir o cadastro e autenticação de clientes;
- oferecer ao cliente cadastrado a possibilidade de favoritar veículos e salvar simulações;
- disponibilizar uma simulação de financiamento de caráter informativo;
- facilitar o contato do cliente interessado com a loja;
- disponibilizar uma área administrativa para gerenciamento dos veículos anunciados.

## 4. Público-alvo e usuários

A plataforma terá inicialmente três contextos de utilização:

### Visitante

Usuário que acessa o site sem possuir uma sessão autenticada.

Poderá navegar pelo catálogo e consultar informações públicas dos veículos.

### Cliente

Usuário cadastrado na plataforma.

O cadastro deverá contemplar inicialmente informações como nome, CPF, e-mail, telefone, data de nascimento, endereço e senha.

Além da navegação pública, o Cliente terá inicialmente as seguintes funcionalidades adicionais:

- favoritar veículos;
- salvar simulações de financiamento para consulta posterior.

### Administrador

Usuário responsável pela administração do conteúdo relacionado aos veículos anunciados na plataforma.

A área administrativa deverá permitir o gerenciamento das informações dos veículos.

A autenticação utiliza perfis de acesso, inicialmente Cliente e Administrador.

## 5. Escopo inicial

O escopo inicial do GhostPay inclui:

- página inicial;
- catálogo de veículos em página própria;
- filtros e ordenações básicas do catálogo;
- página de detalhes de cada veículo;
- consulta da configuração original e das modificações do veículo;
- cadastro de cliente;
- login;
- favoritos do cliente;
- simulação de financiamento;
- simulações salvas do cliente;
- mecanismo de contato com a loja;
- área administrativa;
- gerenciamento dos veículos anunciados.

Não fazem parte do escopo inicial:

- a conclusão da compra e o pagamento integral do veículo;
- opções selecionáveis pelo usuário para montar ou personalizar um veículo. Caso a loja venha a oferecer opções realmente selecionáveis, isso deverá ser especificado em uma Change própria.

## 6. Principais funcionalidades

### Catálogo de veículos

O catálogo terá uma página própria com a listagem completa dos veículos publicados.

O visitante poderá visualizar informações resumidas como modelo, ano, quilometragem e preço.

O catálogo deverá identificar visualmente:

- veículos modificados/preparados, por meio de uma identificação como “Modificado” ou “Preparado”;
- veículos vendidos, que poderão permanecer visíveis, claramente identificados como “Vendido” e indisponíveis para negociação.

Veículos em rascunho não aparecem no catálogo público.

Estão planejados filtros básicos por marca, modelo, ano, faixa de preço e condição (novo/usado), além de ordenações relevantes.

A página inicial poderá futuramente possuir uma seção de veículos em destaque. Os critérios de destaque ainda não foram definidos.

### Detalhes do veículo

Cada veículo poderá possuir uma página própria com informações mais completas, imagens e características relevantes.

É na página de detalhes que ficam, principalmente, a configuração original e os detalhes completos das modificações.

### Configuração original e modificações

O usuário poderá consultar a configuração original do veículo, como marca, modelo, versão, ano, cor, motorização e câmbio.

Veículos modificados poderão apresentar, quando aplicável e quando as informações estiverem disponíveis, dados sobre as modificações realizadas, como preparação do motor, turbo/sobrealimentação, potência, combustível, alterações de câmbio, suspensão, rodas e pneus, freios, interior, modificações estéticas e outras modificações relevantes.

Nem todo veículo possuirá todos esses dados.

A plataforma não deve presumir que uma modificação é legalizada, homologada ou regularizada sem que essa informação esteja explicitamente cadastrada.

### Cadastro de cliente

O usuário poderá criar uma conta informando os dados necessários para seu cadastro.

### Autenticação

Usuários cadastrados poderão realizar login na plataforma. O perfil de acesso determina as funcionalidades disponíveis.

### Área do cliente

O Cliente autenticado poderá favoritar veículos e salvar simulações de financiamento para consulta posterior.

### Simulação de financiamento

O usuário poderá realizar uma simulação de financiamento para obter uma estimativa das condições relacionadas ao veículo selecionado.

A simulação tem finalidade acadêmica e informativa. Ela não representa proposta, aprovação ou contratação real de crédito.

Inicialmente a simulação considera:

- valor do veículo;
- valor da entrada;
- valor a financiar;
- prazos de 12, 24, 36, 48 ou 60 meses;
- taxa de juros mensal fictícia/configurável;
- valor estimado da parcela;
- valor total estimado.

A fórmula e a taxa exatas serão definidas durante a especificação dessa funcionalidade.

### Contato com a loja

Após consultar um veículo e suas condições, o usuário poderá utilizar a plataforma para iniciar contato com a loja.

A negociação e conclusão da venda ocorrerão fora do fluxo de compra do site.

### Administração de veículos

A plataforma possuirá uma área administrativa para gerenciamento dos veículos anunciados, incluindo o estado de cada veículo (Rascunho, Disponível ou Vendido).

As operações e permissões administrativas específicas serão detalhadas quando essa funcionalidade for especificada.

## 7. Requisitos e restrições importantes

- A navegação pelo catálogo não deverá exigir cadastro ou login.
- Veículos em rascunho não deverão ser expostos publicamente.
- Veículos vendidos, quando exibidos, deverão estar claramente identificados e indisponíveis para negociação.
- A regularização de modificações não deverá ser presumida.
- Dados de autenticação e informações pessoais deverão ser tratados de maneira segura.
- Funcionalidades administrativas deverão possuir acesso restrito.
- A plataforma não deverá concluir pagamentos ou vendas de veículos diretamente no escopo inicial.
- Regras ainda não definidas não deverão ser presumidas durante o desenvolvimento.
- Novas funcionalidades deverão ser desenvolvidas incrementalmente.

## 8. Arquitetura tecnológica

O projeto será desenvolvido utilizando o ambiente definido para a disciplina.

A arquitetura prevista inclui:

- interface web em HTML, CSS e JavaScript puro, sem framework de frontend neste momento;
- Xano e XanoScript para desenvolvimento do backend;
- Xano CLI para sincronização entre os arquivos locais e o ambiente Xano;
- XanoScript Language Server para suporte ao desenvolvimento;
- Xano Developer MCP para documentação e validação de XanoScript pelos agentes de IA;
- Visual Studio Code como ambiente de desenvolvimento;
- Git para controle de versão;
- GitHub como repositório remoto, quando utilizado;
- OpenSpec para especificação e organização incremental das mudanças;
- agente de Inteligência Artificial como apoio ao desenvolvimento.

### Protótipo da interface

A pasta `frontend-rascunho/` contém o protótipo original da interface. Ela é uma referência visual e funcional inicial, não uma implementação definitiva, e deve permanecer intacta.

A estrutura definitiva do frontend será criada separadamente e evoluirá incrementalmente durante as Changes. Os arquivos ausentes referenciados pelo protótipo não precisam ser reconstruídos.

### Workspace Xano

O workspace Xano do projeto (“Ghost's Workspace”) já foi conectado ao projeto pelo Xano CLI e sincronizado com a pasta `xano/`, que contém os arquivos XanoScript (`.xs`) do backend.

No momento, o workspace possui apenas a estrutura inicial fornecida pelo Xano: as tabelas `user` e `event_log`, os grupos de API de autenticação e de logs de eventos, funções auxiliares, um addon e exemplos de IA. As estruturas próprias do GhostPay serão acrescentadas incrementalmente pelas Changes.

A pasta `xano/` é versionada no Git. As credenciais do Xano CLI ficam fora do repositório e não devem ser copiadas para ele.

### Imagens

A intenção é utilizar os recursos do Xano para armazenamento e gerenciamento das imagens dos veículos, caso isso se mostre compatível com a arquitetura durante a implementação.

Imagens provisórias poderão ser utilizadas até que a gestão definitiva de imagens seja implementada.

## 9. Princípios de desenvolvimento

O GhostPay deverá ser desenvolvido de maneira incremental.

Funcionalidades relevantes deverão passar pelo fluxo de especificação do OpenSpec antes da implementação.

O desenvolvimento deverá priorizar mudanças pequenas e verificáveis, evitando implementar grandes partes do sistema sem especificação prévia.

Decisões ainda não definidas deverão ser discutidas e especificadas antes de serem incorporadas ao sistema.

## 10. Segurança e integridade

A aplicação deverá proteger informações pessoais e credenciais dos usuários.

Funcionalidades administrativas deverão ser acessíveis somente a usuários autorizados.

Credenciais, tokens e informações sensíveis não deverão ser armazenados diretamente em arquivos versionados no repositório.

## 11. Estratégia de desenvolvimento

O projeto será desenvolvido por funcionalidades incrementais.

O fluxo geral será:

1. analisar o contexto do projeto;
2. explorar a funcionalidade ou problema;
3. propor uma mudança utilizando OpenSpec;
4. revisar a especificação;
5. implementar a mudança;
6. verificar o funcionamento;
7. arquivar a mudança concluída;
8. iniciar a próxima mudança.

### Sequência prevista

A sessão inicial de Explore indicou o catálogo público como ponto de partida, por não depender de autenticação e por estabelecer o conceito de Veículo, do qual as demais funcionalidades dependem.

A sequência prevista, sujeita a revisão a cada Change, é:

1. catálogo público em página própria;
2. detalhes do veículo, com configuração original, modificações e imagens;
3. filtros e ordenação do catálogo;
4. cadastro e login;
5. administração de veículos.

Em seguida: favoritos, simulação de financiamento, simulações salvas, contato com a loja e seção de destaques na página inicial.

## 12. Fonte de verdade e documentação

Os documentos de contexto do projeto deverão orientar as decisões gerais de desenvolvimento.

O OpenSpec será utilizado para registrar as especificações e mudanças incrementais.

O modelo de domínio deverá registrar os principais conceitos e relações do sistema.

Quando houver dúvidas relacionadas ao Xano, XanoScript ou ferramentas utilizadas no ambiente, deverá ser priorizada a documentação oficial e os recursos de documentação disponibilizados pelo Xano Developer MCP.
