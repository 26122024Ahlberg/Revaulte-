# Tasks

## 1. Rotas e recortes

- [x] 1.1 Acrescentar `id` e `usado` a `CartaoVeiculo`, o recorte (`todos`, `usados`, `modificados`) ao `CatalogState` com a variável computada dos cartões exibidos, e fazer a troca de imagem provisória localizar o cartão por `id`; verificar com testes em `frontend/tests/` cobrindo os três recortes, inclusive vendido modificado em `modificados`, e a troca de imagem após mudança de recorte
- [ ] 1.2 Registrar `/estoque`, `/usados` e `/modificados` em `revaulte.py` com títulos e mensagens de vazio próprios, transformar `/catalogo` em redirecionamento para `/estoque` e substituir o redirecionamento da raiz pela página inicial provisória; verificar no navegador cada rota, que `/catalogo` termina em `/estoque` e que `/` mostra a página provisória com link para o estoque

## 2. Menu e página não encontrada

- [x] 2.1 Atualizar `topo()` com a navegação principal (Home, Estoque, Usados e Modificados), marca levando a `/` e `aria-current` no item atual; verificar no navegador acima de 760 px que os quatro itens ficam visíveis no cabeçalho, abrem sem erro e que só o item atual aparece marcado (aprovado visualmente pelo usuário no Safari, desktop)
- [ ] 2.2 Implementar o botão ☰ em qualquer largura e o painel com as seções “Navegação” (só até 760 px) e “Minha conta” (cinco itens “Em breve”, sem link), com `MenuState`, `aria-expanded`/`aria-controls`/`aria-label` e fechamento pelo botão, pela camada atrás do painel, ao escolher item e ao carregar página; verificar a 1280 px que o painel mostra só “Minha conta” e a navegação continua no cabeçalho, e a 375 px que o painel mostra as duas seções, que a navegação funciona e fecha o painel, que os itens “Em breve” não abrem nada e que não há rolagem horizontal — desktop aprovado visualmente pelo usuário no Safari; pendente a verificação no celular e do fechamento do painel
- [ ] 2.3 Registrar a página não encontrada com o layout da Revaulte e link para `/estoque` (confirmar o suporte no Reflex 0.10); verificar abrindo `/pagina-que-nao-existe`

## 3. Verificação integrada

- [x] 3.1 Executar os testes de `frontend/tests/`, `reflex compile` e `openspec validate navegacao-principal --strict`; verificar que todos passam e que o `git diff` não altera `frontend-html/` nem `xano/`
