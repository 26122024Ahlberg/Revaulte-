# Revaulte — Modelo de Domínio

## 1. Visão geral do domínio

O domínio do Revaulte é composto pelos conceitos necessários para apresentar veículos disponíveis para venda, originais ou modificados/preparados, permitir o cadastro e autenticação de clientes, apresentar a configuração original e as modificações dos veículos, realizar simulações de financiamento, oferecer favoritos e simulações salvas aos clientes e permitir o gerenciamento dos anúncios por usuários administrativos.

Cada anúncio representa um veículo real.

Revaulte é o nome oficial do marketplace e do site de veículos. A Revaulte intermedia a descoberta e o contato entre comprador e anunciante; não é proprietária dos veículos anunciados. GhostPay é apenas o nome do grupo acadêmico que desenvolve o projeto e não faz parte do domínio (ver “Identidade nominal” em `docs/project-overview.md`).

Este documento representa os conceitos e relações do sistema em nível de domínio. Ele não define a estrutura física do banco de dados.

---

## 2. Cliente

### Descrição

Representa uma pessoa que se cadastra no Revaulte para possuir uma conta na plataforma.

### Responsabilidades

- manter os dados cadastrais do cliente;
- permitir a identificação do cliente na plataforma;
- participar do processo de autenticação;
- utilizar funcionalidades destinadas a usuários cadastrados.

### Principais atributos conceituais

- nome;
- CPF;
- e-mail;
- telefone;
- data de nascimento;
- endereço;
- credencial de acesso.

### Relações

- um Cliente possui uma Conta de acesso;
- um Cliente poderá possuir Favoritos;
- um Cliente poderá realizar e salvar Simulações de Financiamento;
- um Cliente poderá demonstrar interesse em um Veículo.

### Regras importantes

- o CPF deve identificar unicamente um cliente;
- o e-mail utilizado para acesso não deve pertencer a mais de uma conta;
- informações pessoais devem ser protegidas;
- credenciais de acesso não devem ser armazenadas de forma insegura.

---

## 3. Conta

### Descrição

Representa o acesso autenticado de um usuário ao Revaulte.

### Responsabilidades

- permitir autenticação;
- associar o acesso ao usuário correspondente;
- diferenciar acessos de clientes e acessos administrativos;
- controlar o acesso a funcionalidades protegidas.

### Principais atributos conceituais

- identificação de acesso;
- credencial;
- perfil de acesso;
- situação da conta.

### Relações

- uma Conta está associada a um usuário da plataforma;
- uma Conta possui um perfil de acesso, inicialmente Cliente ou Administrador.

### Regras importantes

- somente usuários autenticados poderão acessar funcionalidades protegidas;
- o perfil Cliente dá acesso às funcionalidades destinadas ao usuário cadastrado;
- o perfil Administrador dá acesso às funcionalidades administrativas;
- funcionalidades administrativas devem exigir autorização adequada;
- visitantes não precisam possuir Conta para navegar pelo catálogo público.

---

## 4. Administrador

### Descrição

Representa um usuário autorizado a acessar a área administrativa do Revaulte.

### Responsabilidades

- acessar funcionalidades administrativas;
- cadastrar veículos;
- atualizar informações dos veículos;
- controlar o estado dos veículos anunciados;
- gerenciar informações necessárias para apresentação dos veículos, incluindo configuração original, modificações e imagens.

### Relações

- um Administrador possui uma Conta com perfil administrativo;
- um Administrador gerencia Veículos.

### Regras importantes

- apenas usuários autorizados poderão acessar a área administrativa;
- operações administrativas não deverão estar disponíveis para visitantes ou clientes sem permissão.

---

## 5. Veículo

### Descrição

Representa um veículo real anunciado no Revaulte.

É um dos conceitos centrais do sistema e reúne as informações necessárias para que o visitante ou cliente conheça o veículo.

Um Veículo pode ser novo ou usado e pode ser original ou modificado/preparado. A condição (novo/usado) e o fato de ser modificado são características independentes.

### Responsabilidades

- representar um veículo anunciado;
- fornecer informações para exibição no catálogo;
- fornecer informações para a página de detalhes;
- apresentar sua configuração original;
- apresentar suas modificações, quando houver;
- servir como referência para uma simulação de financiamento.

### Principais atributos conceituais

- configuração original (ver seção 7);
- condição (novo ou usado);
- quilometragem;
- preço;
- descrição;
- características;
- imagens;
- indicação de veículo modificado/preparado;
- estado.

Outras características específicas poderão ser definidas posteriormente durante a especificação das funcionalidades relacionadas aos veículos.

### Estados

Um Veículo possui inicialmente três estados conceituais:

- **Rascunho**: ainda não publicado e invisível no catálogo público;
- **Disponível**: publicado e disponível para negociação;
- **Vendido**: já vendido; pode continuar visível publicamente, claramente identificado como vendido e indisponível para negociação.

Não existe, neste momento, um estado “Removido”.

### Relações

- um Veículo pode possuir várias Imagens;
- um Veículo possui uma Configuração Original;
- um Veículo pode possuir nenhuma, uma ou várias Modificações;
- um Veículo pode ser utilizado em Simulações de Financiamento;
- um Veículo pode ser favoritado por Clientes;
- um Veículo é gerenciado por meio da área administrativa.

### Regras importantes

- veículos em Rascunho não devem ser expostos publicamente;
- somente veículos no estado Disponível devem ser apresentados como disponíveis para negociação;
- veículos modificados/preparados devem ser identificados como tal no catálogo;
- informações exibidas ao cliente devem corresponder às informações mantidas pela administração;
- detalhes específicos ainda não definidos não devem ser presumidos.

---

## 6. Imagem do Veículo

### Descrição

Representa uma imagem utilizada para apresentar visualmente um veículo no catálogo ou em sua página de detalhes.

### Responsabilidades

- permitir a apresentação visual do veículo;
- compor a galeria de imagens de um veículo.

### Relações

- cada Imagem de Veículo está associada a um Veículo;
- um Veículo pode possuir múltiplas imagens.

### Regras importantes

- imagens provisórias poderão ser utilizadas até que a gestão definitiva de imagens seja especificada e implementada.

---

## 7. Configuração Original do Veículo

### Descrição

Representa as características com que o veículo foi originalmente produzido.

É uma informação descritiva do veículo anunciado. O usuário a consulta; ele não a seleciona nem monta. O Revaulte não é um configurador de veículo novo de montadora.

### Principais atributos conceituais

- marca;
- modelo;
- versão;
- ano;
- cor;
- motorização;
- câmbio.

### Relações

- a Configuração Original pertence a um Veículo.

### Regras importantes

- a Configuração Original deve ser mantida distinta das Modificações realizadas posteriormente;
- opções selecionáveis pelo usuário não fazem parte do modelo atual. Caso venham a ser oferecidas, isso deverá ser especificado em uma Change própria, sem presumir esse comportamento.

---

## 8. Modificação do Veículo

### Descrição

Representa uma alteração realizada no veículo posteriormente à sua configuração original.

A apresentação de veículos modificados/preparados é um ponto importante do Revaulte.

### Responsabilidades

- descrever o que foi alterado no veículo em relação à sua configuração original;
- permitir que o usuário conheça as modificações na página de detalhes;
- registrar, quando informada, a situação de regularização da modificação.

### Áreas de modificação

Quando aplicável e quando as informações estiverem disponíveis, as modificações poderão abranger:

- preparação do motor;
- turbo/sobrealimentação;
- potência;
- combustível;
- alterações de câmbio;
- suspensão;
- rodas e pneus;
- freios;
- interior;
- modificações estéticas;
- outras modificações relevantes.

### Relações

- uma Modificação está relacionada a um Veículo;
- um Veículo pode possuir nenhuma, uma ou várias Modificações.

### Regras importantes

- nem todo veículo possui modificações, e um veículo modificado não precisa possuir dados em todas as áreas;
- a plataforma não deve presumir que uma modificação é legalizada, homologada ou regularizada sem que essa informação esteja explicitamente cadastrada;
- a ausência de informação sobre regularização não deve ser apresentada como regularização;
- os detalhes completos das modificações ficam principalmente na página de detalhes do veículo; no catálogo, basta a identificação de que o veículo é modificado/preparado.

---

## 9. Simulação de Financiamento

### Descrição

Representa uma estimativa de financiamento realizada a partir de um veículo e das condições informadas pelo usuário.

A simulação possui finalidade acadêmica e informativa. Ela não representa proposta, aprovação ou contratação real de crédito.

### Responsabilidades

- utilizar o veículo selecionado como referência;
- receber os parâmetros necessários para a simulação;
- calcular ou apresentar uma estimativa das condições de financiamento;
- informar ao usuário o resultado da simulação;
- poder ser salva por um Cliente para consulta posterior.

### Principais atributos conceituais

Inicialmente a simulação considera:

- valor do veículo;
- valor da entrada;
- valor a financiar;
- prazo, entre 12, 24, 36, 48 ou 60 meses;
- taxa de juros mensal fictícia/configurável;
- valor estimado da parcela;
- valor total estimado.

### Relações

- uma Simulação de Financiamento está relacionada a um Veículo;
- quando salva, está associada a um Cliente.

### Regras importantes

- a simulação não representa aprovação de crédito;
- a simulação não conclui a compra do veículo;
- salvar uma simulação exige um Cliente autenticado;
- a fórmula e a taxa exatas deverão ser especificadas antes da implementação da funcionalidade.

---

## 10. Favorito

### Descrição

Representa a marcação de um Veículo por um Cliente para consulta posterior.

### Relações

- um Favorito relaciona um Cliente a um Veículo;
- um Cliente pode possuir vários Favoritos.

### Regras importantes

- favoritar exige um Cliente autenticado;
- o comportamento de um Favorito quando o veículo muda de estado ainda deverá ser especificado.

---

## 11. Interesse / Contato

### Descrição

Representa a intenção de um visitante ou cliente de entrar em contato com o anunciante a respeito de um veículo.

### Responsabilidades

- permitir que o usuário prossiga para o contato com o anunciante;
- manter o contexto do veículo de interesse quando necessário.

### Relações

- um Interesse pode estar relacionado a um Veículo;
- quando o usuário estiver identificado, poderá estar relacionado a um Cliente.

### Regras importantes

- o contato não representa uma venda concluída;
- a negociação e conclusão da venda ocorrem fora do fluxo de compra da plataforma.

---

## 11-A. Anunciante (planejado)

### Descrição

Representa quem anuncia um veículo na Revaulte: futuramente, particulares, lojas e vendedores profissionais.

### Principais atributos conceituais

- nome de exibição;
- meio de contato autorizado (inicialmente WhatsApp);
- autorização para exibir o contato publicamente.

### Relações

- um Anunciante pode anunciar vários Veículos;
- um Veículo anunciado está associado a um Anunciante;
- futuramente, um Anunciante estará associado a uma Conta.

### Regras importantes

- somente dados que o Anunciante autorizou podem ser exibidos publicamente;
- dados pessoais do Anunciante (CPF, e-mail, endereço) não são exibidos publicamente;
- nenhum dado de contato pode ser inventado.

Este conceito ainda não existe no backend. Será especificado e implementado pela Change `contato-vendedor`, após autorização.

---

## 12. Catálogo

### Descrição

Representa o conjunto de veículos apresentados publicamente no Revaulte, em uma página própria com a listagem completa.

### Responsabilidades

- disponibilizar os veículos para navegação;
- apresentar informações resumidas dos veículos;
- identificar visualmente veículos modificados/preparados e veículos vendidos;
- permitir que o usuário acesse os detalhes de um veículo;
- permitir filtrar e ordenar os veículos.

### Relações

- o Catálogo apresenta Veículos nos estados Disponível e Vendido.

### Regras importantes

- a navegação pelo catálogo não exige autenticação;
- veículos em Rascunho não fazem parte do Catálogo;
- veículos vendidos, quando apresentados, devem estar claramente identificados como “Vendido” e indisponíveis para negociação;
- veículos modificados/preparados devem possuir uma identificação como “Modificado” ou “Preparado”;
- os filtros planejados são marca, modelo, ano, faixa de preço e condição (novo/usado), além de ordenações relevantes;
- a página inicial exibe uma seção de veículos em destaque, separada do Catálogo, com os três veículos Disponíveis cadastrados mais recentemente; veículos vendidos não são destaque.

---

## 13. Relações principais do domínio

De maneira simplificada, os principais conceitos se relacionam da seguinte forma:

Visitante
→ navega pelo Catálogo
→ consulta Veículo
→ consulta Configuração Original e Modificações
→ realiza Simulação de Financiamento
→ entra em Contato com o Anunciante

Cliente
→ possui Conta com perfil Cliente
→ navega pelo Catálogo
→ consulta Veículo
→ consulta Configuração Original e Modificações
→ favorita Veículos
→ realiza e salva Simulações de Financiamento
→ demonstra Interesse / entra em Contato

Administrador
→ possui Conta com perfil Administrador
→ acessa Área Administrativa
→ gerencia Veículos
→ gerencia informações, configuração original, modificações, imagens e estado

Veículo
→ possui Imagens
→ possui Configuração Original
→ pode possuir Modificações
→ participa de Simulações de Financiamento
→ pode ser favoritado
→ pode estar relacionado a manifestações de Interesse / Contato

---

## 14. Limites atuais do modelo

Este modelo representa o entendimento atual do domínio do Revaulte.

Detalhes que ainda não foram definidos, como:

- forma de registrar as modificações e sua situação de regularização (por modificação ou por veículo);
- tratamento de potência e combustível quando diferem entre a configuração original e o estado atual do veículo;
- transições permitidas entre os estados do veículo;
- fórmula da simulação de financiamento, taxa e quem a configura;
- funcionamento detalhado do contato com o anunciante e do chat interno;
- quem pode ser Anunciante, como se cadastra e como os anúncios são moderados;
- permissões específicas da área administrativa e criação do primeiro Administrador;
- critério administrativo de destaque na página inicial (no MVP, os destaques são os três veículos Disponíveis mais recentes);
- existência de opções selecionáveis oferecidas pelo anunciante;

deverão ser definidos incrementalmente por meio das especificações e Changes do OpenSpec.

O modelo de domínio poderá evoluir conforme novas funcionalidades forem especificadas, desde que as mudanças sejam justificadas e mantenham coerência com o objetivo geral do projeto.
