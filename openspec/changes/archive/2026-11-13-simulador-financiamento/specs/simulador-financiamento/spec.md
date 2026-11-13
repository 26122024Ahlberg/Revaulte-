# Spec Delta

## Purpose

Permite que o visitante estime, na página de um veículo Disponível, as parcelas de um financiamento hipotético, sem cadastro, sem integração bancária e sem caráter de proposta de crédito.

## ADDED Requirements

### Requirement: Simulador na página do veículo
A página de um veículo Disponível SHALL exibir a seção “Simular financiamento”, sem exigir cadastro ou login. A página de um veículo Vendido MUST NOT exibir o simulador.

#### Scenario: Veículo disponível
- **WHEN** o visitante abre a página de um veículo Disponível
- **THEN** a seção “Simular financiamento” é exibida

#### Scenario: Veículo vendido
- **WHEN** o visitante abre a página de um veículo Vendido
- **THEN** a seção “Simular financiamento” não é exibida

### Requirement: Valor do veículo automático
O simulador SHALL usar como valor do veículo o preço do anúncio exibido na página, sem permitir que o visitante o altere.

#### Scenario: Valor preenchido
- **WHEN** o simulador é exibido para um veículo de R$ 118.900,00
- **THEN** o valor do veículo mostrado é R$ 118.900,00 e não é editável

### Requirement: Parâmetros ajustáveis
O visitante SHALL poder ajustar o valor da entrada, de zero até um valor menor que o preço do veículo; escolher o prazo entre 12, 24, 36, 48 e 60 parcelas mensais; e ajustar a taxa de juros mensal hipotética, de 0% a 5% ao mês. O simulador SHALL abrir com valores iniciais preenchidos e SHALL aceitar valores digitados no formato brasileiro (vírgula como separador decimal).

#### Scenario: Visitante altera o prazo
- **WHEN** o visitante troca o prazo de 48 para 24 parcelas
- **THEN** o resultado é recalculado para 24 parcelas

### Requirement: Cálculo da estimativa
O simulador SHALL calcular o valor a financiar (preço menos entrada) e a parcela mensal fixa pelo sistema de amortização francês (Tabela Price): parcela = valor financiado × i ÷ (1 − (1 + i)^−n), em que i é a taxa mensal e n o número de parcelas; com taxa zero, parcela = valor financiado ÷ n. SHALL exibir também o total pago (entrada + n × parcela) e o total de juros (total pago − preço). Todos os valores SHALL ser exibidos em reais, arredondados ao centavo, e atualizados a cada alteração válida.

#### Scenario: Cálculo com juros
- **WHEN** o preço é R$ 100.000,00, a entrada R$ 20.000,00, o prazo 48 parcelas e a taxa 1,5% ao mês
- **THEN** o valor a financiar é R$ 80.000,00, a parcela é R$ 2.350,00, o total pago é R$ 132.800,00 e o total de juros é R$ 32.800,00

#### Scenario: Taxa zero
- **WHEN** o valor a financiar é R$ 60.000,00, o prazo 60 parcelas e a taxa 0%
- **THEN** a parcela é R$ 1.000,00 e o total de juros é R$ 0,00

### Requirement: Validação das entradas
Quando a entrada for negativa, igual ou maior que o preço, ou não numérica, ou a taxa estiver fora do intervalo permitido ou não for numérica, o simulador SHALL exibir uma mensagem explicando o problema e MUST NOT exibir um resultado calculado com valores inválidos.

#### Scenario: Entrada maior que o preço
- **WHEN** o visitante informa uma entrada maior que o preço do veículo
- **THEN** o simulador informa que a entrada deve ser menor que o valor do veículo e não exibe parcela

#### Scenario: Taxa inválida
- **WHEN** o visitante informa a taxa “abc” ou 12%
- **THEN** o simulador informa o intervalo aceito e não exibe parcela

### Requirement: Aviso de simulação hipotética
O simulador SHALL exibir, sempre junto ao resultado, o aviso de que se trata de uma estimativa hipotética, com taxa ilustrativa, que não inclui impostos, tarifas e seguros e que não representa proposta, aprovação ou contratação de crédito. O simulador MUST NOT enviar dados a terceiros, MUST NOT apresentar a taxa como oferta da Revaulte ou de instituição financeira e MUST NOT oferecer contratação.

#### Scenario: Visitante consulta o resultado
- **WHEN** o simulador exibe uma parcela estimada
- **THEN** o aviso de simulação hipotética está visível na mesma seção
