# Tasks

## 1. Etapa A: página com a listagem atual (sem alterar o Xano)

- [ ] 1.1 Confirmar com um teste mínimo no Reflex 0.10 a rota `/veiculo/[id]` e a leitura do parâmetro no estado; verificar abrindo `/veiculo/1` e `/veiculo/abc` e registrando o valor lido — rota registrada como `/veiculo/[veiculo_id]`; o parâmetro chega em `router.page.params` (conferido em `.web/utils/state.js`), com leitura do caminho como reserva; testes cobrem a leitura; pendente a abertura no navegador
- [x] 1.2 Implementar em `state.py` `buscar_veiculo(id)` sobre `GET /vehicles`, o `DetalheVeiculo` e o `DetalheState` com situações carregando, encontrado, não encontrado e erro; verificar com testes em `frontend/tests/` (id existente, inexistente, inválido, falha HTTP, tempo esgotado, vendido, modificado sem modificações)
- [ ] 1.3 Implementar a página em `components.py`/`revaulte.py`: foto com imagem provisória, título, ano, km, condição, preço, selos, seção de modificações, “Voltar ao estoque”, “Tenho interesse” demonstrativo (ausente se vendido) e mensagens de não encontrado e erro; verificar no navegador os cenários correspondentes da spec — implementado; mensagem do interesse ajustada para “anunciante”; testes de componente passam; pendente a verificação no navegador
- [ ] 1.4 Tornar os cartões links para `/veiculo/<id>` com foco visível; verificar no navegador por clique e teclado (Tab + Enter) a partir de `/estoque`, `/usados` e `/modificados` — implementado também nos destaques da Home; pendente a verificação no navegador

## 2. Etapa B: backend (executar somente após autorização do usuário)

- [ ] 2.1 Consultar no Xano Developer MCP a sintaxe de parâmetro de rota, consulta única, referência entre tabelas e resposta 404; registrar as construções confirmadas
- [ ] 2.2 Acrescentar os campos opcionais a `xano/table/vehicle.xs` e criar `xano/table/vehicle_modification.xs`; verificar com `xano_validate_xanoscript` sem erros
- [ ] 2.3 Criar o endpoint `GET vehicles/{vehicle_id}` em `xano/api/catalog/`; verificar com `xano_validate_xanoscript` sem erros
- [ ] 2.4 Enviar as alterações pelo Xano CLI e inserir dados técnicos e modificações de teste pelo painel; verificar por requisições sem token: 200 com campos previstos para Disponível e Vendido, 404 idêntico para Rascunho e inexistente, e `GET /vehicles` inalterado

## 3. Troca para o endpoint de detalhe

- [ ] 3.1 Trocar `buscar_veiculo` para `GET /vehicles/{vehicle_id}` e exibir cor, motorização, câmbio, descrição e modificações por área; verificar com os testes atualizados e no navegador os cenários de dados técnicos parciais e modificações cadastradas
- [ ] 3.2 Registrar em `docs/domain-model.md` as áreas de modificação adotadas e que a regularização não é modelada nesta etapa; verificar o texto

## 4. Verificação integrada

- [ ] 4.1 Percorrer todos os cenários de `specs/detalhes-veiculo/spec.md`, inspecionar as mensagens do WebSocket para confirmar que nenhum dado de Rascunho chega ao navegador, executar os testes, `reflex compile` e `openspec validate detalhes-veiculo --strict`; verificar que tudo passa e que `frontend-html/` não foi alterado
