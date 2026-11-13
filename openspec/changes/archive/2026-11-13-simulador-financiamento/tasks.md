# Tasks

## 1. Definições

- [x] 1.1 Submeter ao usuário a fórmula (Tabela Price), os valores iniciais, os limites e o texto do aviso; verificar a aprovação antes de implementar — implementação autorizada pelo usuário em 21/10/2026 com os valores propostos no design; pendente a revisão do texto do aviso e dos valores — fórmula, valores iniciais, limites e texto do aviso revisados e aprovados pelo usuário em 13/11/2026

## 2. Cálculo

- [x] 2.1 Implementar `calcular_financiamento` e a leitura de valores no formato brasileiro em `state.py`; verificar com testes em `frontend/tests/` os dois cenários de cálculo da spec, entrada zero, entrada igual e maior que o preço, taxa fora do intervalo e textos inválidos

## 3. Interface

- [x] 3.1 Implementar o `SimuladorState` e a seção “Simular financiamento” na página do veículo, ausente para Vendido; verificar com testes de componente e no navegador cada cenário da spec, inclusive teclado e celular — implementado; testes de componente passam; cálculo e resultado confirmado pelo usuário no Safari (desktop) em 27/10/2026; pendente teclado e celular — verificado em 13/11/2026 no Safari 26 do macOS, por automação WebDriver (`safaridriver`) sobre o servidor local, com medições registradas: pelo teclado, a 1280 e a 375 px, a entrada digitada recalcula a parcela, o prazo 12x é escolhido com Enter (`aria-pressed`), a taxa 9% mostra o erro e 1,5% volta ao resultado, sem erros de JavaScript; o simulador não aparece para Vendido (teste de componente; não há veículo Vendido no Xano)
- [x] 3.2 Ajustar `styles.css` na identidade preta e vermelha; verificar no navegador a 375 px e no desktop, sem rolagem horizontal — implementado (2 colunas, 1 coluna até 860 px); desktop confirmado pelo usuário no Safari (desktop) em 27/10/2026; pendente 375 px sem rolagem horizontal — verificado em 13/11/2026 no Safari 26 do macOS, por automação WebDriver (`safaridriver`) sobre o servidor local, com medições registradas: a 375 px o simulador ficava cortado à direita (formulário até 434 px, escondido pelo `overflow` da página); corrigido em 13/11/2026 com `minmax(0, 1fr)` na coluna única (até 860 px) e teste de regressão em `tests/test_simulador.py`; após a correção, nenhum elemento fora da tela em 320, 375, 560, 980 e 1280 px

## 4. Documentação e verificação

- [x] 4.1 Registrar em `docs/domain-model.md` a fórmula, a taxa inicial e os limites adotados; verificar o texto
- [x] 4.2 Executar os testes, `reflex compile` e `openspec validate simulador-financiamento --strict`; verificar que passam e que `frontend-html/` e `xano/` não foram alterados — verificado em 21/10/2026 na auditoria do OpenSpec: 97 testes, `reflex compile` e `openspec validate --all --strict` passam; `git diff` sem alterações em `xano/` e `frontend-html/`
