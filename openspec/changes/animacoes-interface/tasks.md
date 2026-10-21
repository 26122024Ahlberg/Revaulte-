# Tasks

## 1. Animações em CSS

- [ ] 1.1 Acrescentar em `styles.css` as animações de entrada (somente `opacity` e `transform`, até 0,5 s) para seções e cartões, as microinterações de cartões, botões e menu e o foco visível (`:focus-visible`); verificar no navegador em 1280, 980 e 375 px que não há rolagem horizontal nem deslocamento do layout
- [ ] 1.2 Substituir o texto estático de carregamento por indicação animada com o texto mantido (região `aria-live` existente); verificar no navegador e com o VoiceOver do macOS que o texto é anunciado
- [ ] 1.3 Garantir que `@media (prefers-reduced-motion: reduce)` desative entrada, deslocamento e rotação; verificar ativando “Reduzir movimento” no macOS e recarregando cada página

## 2. Verificação

- [ ] 2.1 Executar `reflex compile`, os testes de `frontend/tests/` e `openspec validate animacoes-interface --strict`; verificar no Safari que o console não mostra erros e que o desempenho de rolagem permanece fluido
