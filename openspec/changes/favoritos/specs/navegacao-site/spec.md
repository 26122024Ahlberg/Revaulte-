# Spec Delta

## MODIFIED Requirements

### Requirement: Menu da conta
Todas as páginas públicas SHALL exibir, no canto superior direito do cabeçalho e em qualquer largura de tela, um botão de menu (☰) acessível que informa se o menu está aberto. O painel SHALL conter a seção “Minha conta”, com itens conforme a sessão confirmada no backend e os links “Anunciar veículo”, “Meus anúncios” e “Favoritos” (para `/favoritos`). Nesta versão nenhum item está como “Em breve”; um item futuro sem página implementada MUST ser identificado como “Em breve”, sem link. “Painel administrativo” MUST NOT aparecer a visitante nem a Cliente.

#### Scenario: Abrir o menu da conta
- **WHEN** um visitante sem sessão aciona o botão ☰
- **THEN** a seção “Minha conta” exibe “Entrar”, “Cadastrar”, “Anunciar veículo”, “Meus anúncios” e “Favoritos”, todos como links

#### Scenario: Visitante aciona Anunciar veículo
- **WHEN** um visitante sem sessão aciona “Anunciar veículo” no painel
- **THEN** o painel é fechado e ele é levado a `/entrar?proximo=/anunciar`

#### Scenario: Visitante aciona Favoritos
- **WHEN** um visitante sem sessão aciona “Favoritos” no painel
- **THEN** o painel é fechado e ele é levado a `/entrar?proximo=/favoritos`

#### Scenario: Cliente abre o menu da conta
- **WHEN** um Cliente autenticado aciona o botão ☰
- **THEN** a seção “Minha conta” exibe “Minha conta”, “Anunciar veículo”, “Meus anúncios”, “Favoritos” e “Sair”, e não exibe “Entrar”, “Cadastrar” nem “Painel administrativo”

#### Scenario: Administrador abre o menu da conta
- **WHEN** um Administrador autenticado aciona o botão ☰
- **THEN** a seção exibe “Minha conta”, “Painel administrativo”, “Anunciar veículo”, “Meus anúncios”, “Favoritos” e “Sair”

#### Scenario: Item ainda não disponível
- **WHEN** o painel exibe um item cuja página ainda não foi implementada
- **THEN** nenhuma página é aberta ao acioná-lo e ele continua identificado como “Em breve”

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
- **THEN** o painel exibe a seção “Navegação” com os quatro itens e a seção “Minha conta” com “Entrar”, “Cadastrar”, “Anunciar veículo”, “Meus anúncios” e “Favoritos”, todos como links

#### Scenario: Painel do Administrador no celular
- **WHEN** em uma tela de 375 px um Administrador autenticado abre o painel
- **THEN** o painel exibe a seção “Navegação” com os quatro itens e a seção “Minha conta” com “Minha conta”, “Painel administrativo”, “Anunciar veículo”, “Meus anúncios”, “Favoritos” e “Sair”, sem rolagem horizontal
