# Proposal

## Why

A simulação de financiamento já faz parte do escopo inicial (`docs/project-overview.md`, seções 5 e 6, e `docs/domain-model.md`, seção 9). Na página do veículo, ela ajuda o visitante a avaliar se um clássico, esportivo ou preparado cabe no seu orçamento. Como o cálculo é informativo e não depende de dados novos, a simulação pode ser entregue para a apresentação sem alterar o backend, depois da página individual do veículo.

## What Changes

- Seção “Simular financiamento” na página do veículo (`/veiculo/<id>`), somente para veículos Disponíveis.
- Valor do veículo preenchido automaticamente com o preço do anúncio, sem edição.
- Entrada ajustável, prazo escolhido entre 12, 24, 36, 48 e 60 parcelas e taxa de juros mensal hipotética ajustável.
- Cálculo do valor a financiar, da parcela estimada, do total pago e do total de juros, atualizado a cada alteração.
- Validação das entradas com mensagens em português.
- Aviso explícito e sempre visível de que a simulação é hipotética e não representa proposta, aprovação ou contratação de crédito.

### Fora do escopo

- Integração com bancos ou financeiras, análise de crédito, envio de proposta.
- Salvar simulações (exige cadastro e login, Change futura).
- Taxa definida pela administração; IOF, tarifas, seguros e outros encargos.
- Alterações no backend Xano.

## Capabilities

### New Capabilities

- `simulador-financiamento`: simulação informativa de financiamento na página do veículo, com entradas, validação, resultado e aviso.

### Modified Capabilities

Nenhuma.

## Impact

- **Frontend Reflex**: estado e função de cálculo do simulador em `state.py`, componentes em `components.py`, estilos em `styles.css`, testes em `frontend/tests/`.
- **Backend Xano**: nenhum; usa o preço que a página do veículo já recebe.
- **Documentação**: registrar em `docs/domain-model.md` a fórmula, os limites e a taxa inicial adotados (hoje marcados como “a definir”).
- **Dependências**: depois de `detalhes-veiculo` (etapa A basta).
