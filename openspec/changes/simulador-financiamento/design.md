# Design

## Context

Requisitos: ver `specs/simulador-financiamento/spec.md`. A página do veículo (Change `detalhes-veiculo`) já terá o preço do anúncio no estado. O domínio prevê prazos de 12 a 60 meses e taxa “fictícia/configurável”, mas deixa a fórmula e a taxa “a definir” (`docs/domain-model.md`, seções 9 e 14). Esta Change propõe essas definições para revisão do usuário.

## Goals / Non-Goals

**Goals:** cálculo correto e testável em Python puro; nenhuma dependência nova; nenhum dado enviado a terceiros.

**Non-Goals:** salvar simulações, taxa administrável, encargos (IOF, tarifas, seguro), integração bancária.

## Decisions

### 1. Tabela Price com `Decimal`

Função pura `calcular_financiamento(preco, entrada, parcelas, taxa_mensal)` em `state.py`, com `Decimal` e arredondamento `ROUND_HALF_UP` ao centavo só na exibição final da parcela; total pago e juros calculados a partir da parcela arredondada, para que os números exibidos fechem entre si. Taxa zero tratada separadamente (evita divisão por zero).

Alternativa: sistema SAC (parcelas decrescentes). Descartada: a parcela fixa é a forma mais comum em financiamento de veículos e mais simples de apresentar.

### 2. Valores iniciais e limites (propostos, a confirmar pelo usuário)

- Entrada inicial: 20% do preço, arredondada a reais.
- Prazo inicial: 48 parcelas; opções 12, 24, 36, 48 e 60 (do domínio).
- Taxa inicial: 1,50% ao mês, apresentada como “taxa ilustrativa”; aceita de 0% a 5% ao mês, com até duas casas decimais.

### 3. Estado e componentes

`SimuladorState` guarda os textos digitados (entrada e taxa) e o prazo; um `@rx.var` calcula o resultado ou a mensagem de erro, para que a validação use exatamente o que o visitante digitou. A leitura aceita vírgula decimal e pontos de milhar (“20.000,50”). O estado é reiniciado ao abrir outro veículo. Prazo como botões de opção (acessíveis por teclado), entrada e taxa como campos de texto com rótulos visíveis. Resultado em região `aria-live="polite"`.

### 4. Aviso

Texto fixo: “Simulação hipotética, com taxa ilustrativa. Não inclui impostos, tarifas e seguros e não representa proposta, aprovação ou contratação de crédito.” Revisado pelo usuário antes de concluir.

## Risks / Trade-offs

- [Visitante entender a taxa como oferta] → rótulo “taxa ilustrativa” e aviso sempre visível junto ao resultado.
- [Diferença de centavos em relação a calculadoras bancárias] → aceitável; o caso de teste da spec fixa o arredondamento adotado.
- [Recalcular a cada tecla gera eventos ao servidor] → volume pequeno; usar atualização ao sair do campo se houver atraso perceptível.
