# Spec Delta

## Purpose

Permite que o visitante navegue entre as páginas públicas da Revaulte por um menu principal consistente, incluindo páginas dedicadas a veículos usados e a veículos modificados, sem links quebrados.

## ADDED Requirements

### Requirement: Navegação principal
Todas as páginas públicas SHALL exibir a navegação principal com os itens Home, Estoque, Usados e Modificados, nessa ordem, e com a marca Revaulte levando à Home. Em telas com mais de 760 px de largura, os quatro itens SHALL ficar visíveis no cabeçalho. O item correspondente à página atual SHALL ser identificado visualmente e para tecnologias assistivas.

#### Scenario: Visitante usa a navegação principal
- **WHEN** o visitante aciona qualquer item da navegação principal
- **THEN** a página correspondente é aberta sem erro

#### Scenario: Página atual identificada
- **WHEN** o visitante está na página de Usados
- **THEN** o item “Usados” aparece como página atual e os demais não

#### Scenario: Navegação em tela larga
- **WHEN** a página é exibida em uma tela com mais de 760 px de largura
- **THEN** Home, Estoque, Usados e Modificados aparecem no cabeçalho sem precisar abrir nenhum menu

### Requirement: Menu da conta
Todas as páginas públicas SHALL exibir, no canto superior direito do cabeçalho e em qualquer largura de tela, um botão de menu (☰) identificado para tecnologias assistivas, que informa se o menu está aberto ou fechado. O painel aberto SHALL conter a seção “Minha conta” com Meu perfil, Anunciar veículo, Meus anúncios, Favoritos e Entrar / Cadastrar. Enquanto essas funcionalidades não forem implementadas, cada item SHALL ser identificado como “Em breve”, MUST NOT ser um link nem levar a página inexistente, e MUST NOT simular login, cadastro ou anúncio.

#### Scenario: Abrir o menu da conta
- **WHEN** o visitante aciona o botão ☰
- **THEN** o painel exibe a seção “Minha conta” com os cinco itens, cada um identificado como “Em breve”

#### Scenario: Item ainda não disponível
- **WHEN** o visitante tenta acionar “Favoritos” no painel
- **THEN** nenhuma página é aberta e o item continua identificado como “Em breve”

#### Scenario: Fechar o menu
- **WHEN** o painel está aberto e o visitante aciona novamente o botão ☰, clica fora do painel ou abre outra página
- **THEN** o painel é fechado

### Requirement: Menu em tela estreita
Em telas de até 760 px de largura, a navegação principal SHALL sair do cabeçalho e o painel do botão ☰ SHALL reunir as seções “Navegação”, com Home, Estoque, Usados e Modificados e a página atual identificada, e “Minha conta”, sem remover nenhuma opção. A página MUST NOT apresentar rolagem horizontal.

#### Scenario: Navegar pelo celular
- **WHEN** em uma tela de 375 px o visitante abre o painel e aciona “Modificados”
- **THEN** a página de Modificados é aberta, o painel é fechado e não há rolagem horizontal

#### Scenario: Painel completo no celular
- **WHEN** em uma tela de 375 px o visitante abre o painel
- **THEN** o painel exibe a seção “Navegação” com os quatro itens e a seção “Minha conta” com os cinco itens

### Requirement: Página inicial provisória
Até a implementação da página inicial completa, o endereço `/` SHALL exibir uma página inicial simples com a marca Revaulte, uma frase sobre a especialidade da loja e um link para o estoque, sem simular seções ou conteúdos ainda não implementados.

#### Scenario: Visitante abre a raiz
- **WHEN** o visitante abre `/`
- **THEN** a página inicial provisória é exibida, com o item Home marcado no menu e um link para `/estoque`

### Requirement: Estoque em rota própria
O catálogo completo SHALL ser acessível em `/estoque`. O endereço `/catalogo` SHALL continuar válido, redirecionando para `/estoque`.

#### Scenario: Acesso ao estoque
- **WHEN** o visitante abre `/estoque`
- **THEN** a listagem completa do catálogo público é exibida

#### Scenario: Endereço antigo do catálogo
- **WHEN** o visitante abre `/catalogo`
- **THEN** ele é levado a `/estoque`

### Requirement: Página de veículos usados
A página `/usados` SHALL exibir somente os veículos do catálogo público com a condição Usado, mantendo os selos, estados e imagens do catálogo.

#### Scenario: Somente usados
- **WHEN** existem no catálogo veículos novos e usados e o visitante abre `/usados`
- **THEN** somente os veículos usados são exibidos

#### Scenario: Nenhum veículo usado
- **WHEN** o catálogo não contém veículos usados e o visitante abre `/usados`
- **THEN** a página exibe uma mensagem informando que não há veículos usados no momento

### Requirement: Página de veículos modificados
A página `/modificados` SHALL exibir somente os veículos do catálogo público indicados como modificados, independentemente da condição e do estado.

#### Scenario: Somente modificados
- **WHEN** existem no catálogo veículos originais e modificados e o visitante abre `/modificados`
- **THEN** somente os veículos modificados são exibidos, inclusive os vendidos

#### Scenario: Nenhum veículo modificado
- **WHEN** o catálogo não contém veículos modificados e o visitante abre `/modificados`
- **THEN** a página exibe uma mensagem informando que não há veículos modificados no momento

### Requirement: Endereço inexistente
Um endereço que não corresponde a nenhuma página SHALL exibir uma página “não encontrada” com a identidade da Revaulte, o menu principal e um link para o estoque.

#### Scenario: Visitante abre endereço inexistente
- **WHEN** o visitante abre `/pagina-que-nao-existe`
- **THEN** a página informa que o endereço não foi encontrado e oferece um link para o estoque
