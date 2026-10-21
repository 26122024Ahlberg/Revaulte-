# Proposal

## Why

O site da Revaulte tem hoje uma única página (`/catalogo`) e um topo com um só item. Para a apresentação do MVP, o visitante precisa navegar entre Home, Estoque, Usados e Modificados sem links quebrados, e a Revaulte, especializada em clássicos, esportivos e preparados, precisa destacar os veículos usados e os modificados em páginas próprias.

## What Changes

- Navegação principal com os itens Home, Estoque, Usados e Modificados em todas as páginas, visível no cabeçalho em telas largas e com o item atual identificado.
- Botão de menu (☰) no canto superior direito, em telas largas e estreitas, que abre o painel “Minha conta” com Meu perfil, Anunciar veículo, Meus anúncios, Favoritos e Entrar / Cadastrar, todos identificados como “Em breve” e sem link enquanto não forem implementados.
- Em telas estreitas, a navegação principal sai do cabeçalho e o mesmo painel reúne as seções “Navegação” e “Minha conta”.
- O catálogo passa a ser servido em `/estoque` (rótulo “Estoque”); `/catalogo` continua funcionando como redirecionamento para `/estoque`.
- Página `/usados`: o catálogo exibindo somente veículos usados.
- Página `/modificados`: o catálogo exibindo somente veículos indicados como modificados (campo `is_modified` já existente).
- Página “não encontrada” com a identidade da Revaulte e caminho de volta, para endereços inexistentes.
- A raiz `/` deixa de redirecionar e passa a exibir uma página inicial provisória e simples (marca, frase curta e link para o estoque), identificada no código como provisória e substituída pela Change `pagina-inicial`.

### Fora do escopo

- Página inicial, pesquisa e filtros escolhidos pelo visitante, página de detalhes e animações (Changes próprias).
- Implementação de perfil, anúncios, favoritos, login e cadastro; seus itens só aparecem desabilitados, como “Em breve”.
- Itens de menu para Financiamento e Contato.
- Qualquer alteração no backend Xano.

## Capabilities

### New Capabilities

- `navegacao-site`: menu principal, rotas do estoque, páginas de Usados e Modificados e tratamento de endereços inexistentes.

### Modified Capabilities

Nenhuma. Os requisitos de `catalogo-publico` (estados, selos, imagem, visibilidade) valem igualmente para `/estoque`, `/usados` e `/modificados`.

## Impact

- **Frontend Reflex**: `revaulte.py` (rotas), `components.py` (topo e página não encontrada), `state.py` (recorte por condição ou modificação sobre a lista já carregada) e `assets/styles.css` (menu em telas estreitas).
- **Backend Xano**: nenhum impacto; reutiliza `GET /vehicles`.
- **Dependência**: aplicar depois de concluir e arquivar a Change `catalogo-publico`.
