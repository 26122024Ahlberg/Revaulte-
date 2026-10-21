# Tasks

## 1. Decisões e domínio

- [ ] 1.1 Submeter ao usuário a mudança de “loja” para “marketplace com anunciantes” e quem pode ser anunciante (a própria Revaulte, lojistas parceiros, particulares); após a aprovação, atualizar `docs/project-overview.md` e `docs/domain-model.md` (Anunciante, Veículo → Anunciante, Interesse/Contato); verificar o texto com o usuário — definição de marketplace aprovada pelo usuário em 21/10/2026 (particulares, lojas e vendedores profissionais) e registrada nos documentos, com o Anunciante como conceito planejado; pendente a revisão do texto pelo usuário

## 2. Backend (executar somente após autorização do usuário)

- [ ] 2.1 Confirmar no Xano Developer MCP a sintaxe de referência entre tabelas e saída condicional; criar `xano/table/seller.xs` e o campo `seller_id` em `vehicle.xs`; verificar com `xano_validate_xanoscript` sem erros
- [ ] 2.2 Incluir os dados públicos do anunciante no endpoint de detalhe; verificar com `xano_validate_xanoscript` e, após o envio pelo Xano CLI, por requisições sem token: nome e número só com autorização, nenhum dado de contato em `GET /vehicles` nem em veículo Vendido
- [ ] 2.3 Cadastrar pelo painel do Xano anunciantes reais que autorizaram a exibição; verificar que nenhum contato fictício foi cadastrado

## 3. Frontend

- [ ] 3.1 Trocar o “Tenho interesse” demonstrativo pelo bloco do anunciante e pelo link do WhatsApp; verificar com testes em `frontend/tests/` (com e sem autorização, sem anunciante, vendido) e no navegador

## 4. Verificação

- [ ] 4.1 Após o arquivamento de `detalhes-veiculo`, acrescentar o delta MODIFIED de “Interesse demonstrativo”; executar os testes, `reflex compile` e `openspec validate contato-vendedor --strict`; verificar que passam
