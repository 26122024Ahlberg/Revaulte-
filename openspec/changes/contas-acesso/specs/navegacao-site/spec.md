# Spec Delta

## MODIFIED Requirements

### Requirement: Menu da conta
Toda página pública SHALL exibir, no alto à direita do cabeçalho, em qualquer largura, um botão de menu (☰) acessível que informa se está aberto. O painel SHALL ter a seção “Minha conta”, com itens conforme a sessão confirmada no backend (visitante, Cliente ou Administrador), e Anunciar veículo, Meus anúncios e Favoritos, que, até serem implementados, SHALL aparecer como “Em breve”, MUST NOT ser links nem simular anúncio ou favorito. Visitante e Cliente MUST NOT ver “Painel administrativo”.

#### Scenario: Abrir o menu da conta
- **WHEN** um visitante sem sessão aciona o botão ☰
- **THEN** a seção “Minha conta” exibe “Entrar” (link para `/entrar`), “Cadastrar” (link para `/cadastro`) e Anunciar veículo, Meus anúncios e Favoritos identificados como “Em breve”

#### Scenario: Cliente abre o menu da conta
- **WHEN** um Cliente autenticado aciona o botão ☰
- **THEN** a seção “Minha conta” exibe “Minha conta” (link para `/conta`) e “Sair”, os itens “Em breve” e não exibe “Entrar”, “Cadastrar” nem “Painel administrativo”

#### Scenario: Administrador abre o menu da conta
- **WHEN** um Administrador autenticado aciona o botão ☰
- **THEN** a seção “Minha conta” exibe “Minha conta” (link para `/conta`), “Painel administrativo” (link para `/admin`) e “Sair”, além dos itens “Em breve”

#### Scenario: Item ainda não disponível
- **WHEN** o visitante tenta acionar “Favoritos” no painel
- **THEN** nenhuma página é aberta e o item continua identificado como “Em breve”

#### Scenario: Fechar o menu
- **WHEN** o painel está aberto e o visitante aciona novamente o botão ☰, clica fora do painel ou abre outra página
- **THEN** o painel é fechado

### Requirement: Menu em tela estreita
Em telas de até 760 px de largura, a navegação principal SHALL sair do cabeçalho e o painel do botão ☰ SHALL reunir as seções “Navegação”, com Home, Estoque, Usados e Modificados e a página atual identificada, e “Minha conta”, com os itens correspondentes à sessão, sem remover nenhuma opção. A página MUST NOT apresentar rolagem horizontal.

#### Scenario: Navegar pelo celular
- **WHEN** em uma tela de 375 px o visitante abre o painel e aciona “Modificados”
- **THEN** a página de Modificados é aberta, o painel é fechado e não há rolagem horizontal

#### Scenario: Painel completo no celular
- **WHEN** em uma tela de 375 px um visitante sem sessão abre o painel
- **THEN** o painel exibe a seção “Navegação” com os quatro itens e a seção “Minha conta” com “Entrar”, “Cadastrar” e os três itens “Em breve”

#### Scenario: Painel do Administrador no celular
- **WHEN** em uma tela de 375 px um Administrador autenticado abre o painel
- **THEN** o painel exibe a seção “Navegação” com os quatro itens e a seção “Minha conta” com “Minha conta”, “Painel administrativo”, “Sair” e os três itens “Em breve”, sem rolagem horizontal
