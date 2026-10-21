# Tasks

## 1. Destaques

- [x] 1.1 Acrescentar o recorte `destaques` (3 primeiros não vendidos) a `aplicar_recorte`; verificar com testes em `frontend/tests/` (cinco disponíveis, vendido mais recente, dois disponíveis, nenhum disponível) e que os testes do catálogo continuam passando

## 2. Página inicial

- [ ] 2.1 Salvar as três imagens do carrossel (Pexels, licença verificada) em `frontend/assets/`, remover `hero.jpg` e registrar origem e licença no `frontend/README.md`; verificar o tamanho dos arquivos, que são servidos e a aprovação visual do usuário
- [ ] 2.2 Implementar o `CarrosselState` (anterior, próximo, ir para, reinício no carregamento) e em `components.py` o banner em carrossel (três slides, setas, indicadores, frase de impacto e botão “Explorar estoque” para `/estoque`), com testes em `frontend/tests/` da navegação circular e da estrutura dos slides, a seção de destaques com estados e link para o estoque, e a seção de proposta; registrar a página em `/` no lugar do redirecionamento; verificar no navegador cada cenário de `specs/pagina-inicial/spec.md`, inclusive bloqueando a imagem do banner e simulando falha da API com `REVAULTE_CATALOG_API_URL` inválido
- [ ] 2.3 Ajustar `styles.css` (banner, seções, animações leves com movimento reduzido, responsividade a 980 e 560 px); verificar no navegador nas três larguras, sem rolagem horizontal, e com “Reduzir movimento” ativado no macOS
- [ ] 2.4 Submeter ao usuário o texto da frase de impacto e da seção de proposta; verificar a aprovação antes de concluir

## 3. Documentação e verificação

- [x] 3.1 Registrar em `docs/project-overview.md` e `docs/domain-model.md` o critério de destaque adotado (3 Disponíveis mais recentes); verificar o texto
- [x] 3.2 Executar os testes, `reflex compile` e `openspec validate pagina-inicial --strict`; verificar que passam e que `frontend-html/` e `xano/` não foram alterados
