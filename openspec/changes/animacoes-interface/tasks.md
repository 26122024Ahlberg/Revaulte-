# Tasks

## 1. Animações em CSS

- [ ] 1.1 Acrescentar em `styles.css` as animações de entrada (somente `opacity` e `transform`, até 0,5 s) para seções e cartões, as microinterações de cartões, botões e menu e o foco visível (`:focus-visible`); verificar no navegador em 1280, 980 e 375 px que não há rolagem horizontal nem deslocamento do layout — implementado (entrada dos cartões em cascata, títulos, página do veículo e mensagens; foto do cartão com leve zoom; brilho nos botões; painel do menu deslizando); pendente a verificação no navegador
- [ ] 1.2 Substituir o texto estático de carregamento por indicação animada com o texto mantido (região `aria-live` existente); verificar no navegador e com o VoiceOver do macOS que o texto é anunciado — implementado (anel animado com `aria-hidden` e texto mantido); teste automatizado passa; pendente o VoiceOver
- [ ] 1.3 Garantir que `@media (prefers-reduced-motion: reduce)` desative entrada, deslocamento e rotação; verificar ativando “Reduzir movimento” no macOS e recarregando cada página — implementado (regra global mais bloco que anula `transform`); teste automatizado confere as regras; pendente a verificação no macOS

## 2. Verificação

- [ ] 2.1 Executar `reflex compile`, os testes de `frontend/tests/` e `openspec validate animacoes-interface --strict`; verificar no Safari que o console não mostra erros e que o desempenho de rolagem permanece fluido — reconferido em 27/10/2026: `reflex compile`, 97 testes e `openspec validate --all --strict` passam; pendente a verificação no Safari
