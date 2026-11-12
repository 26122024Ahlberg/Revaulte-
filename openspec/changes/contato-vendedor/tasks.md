# Tasks

## 1. Decisões e domínio

- [x] 1.1 Submeter ao usuário a mudança de “loja” para “marketplace com anunciantes” e quem pode ser anunciante (a própria Revaulte, lojistas parceiros, particulares); após a aprovação, atualizar `docs/project-overview.md` e `docs/domain-model.md` (Anunciante, Veículo → Anunciante, Interesse/Contato); verificar o texto com o usuário — definição de marketplace aprovada pelo usuário em 21/10/2026 (particulares, lojas e vendedores profissionais) e registrada nos documentos, com o Anunciante como conceito planejado; pendente a revisão do texto pelo usuário — texto e conceito aprovados pelo usuário em 27/10/2026 (marketplace que conecta compradores e anunciantes; publicação pelos próprios usuários após cadastro e login, em Change futura)

## 2. Backend (executar somente após autorização do usuário)

- [x] 2.1 Confirmar no Xano Developer MCP a sintaxe de referência entre tabelas e saída condicional; criar `xano/table/seller.xs` e o campo `seller_id` em `vehicle.xs`; verificar com `xano_validate_xanoscript` sem erros — feito em 07/11/2026 (documentação XanoScript 2.7.1: `sensitive = true`, `{ table = "seller" }`, `conditional`, `|set`, `|unset`); `seller_id` opcional no fim do esquema, com índice; validação sem erros nem avisos
- [ ] 2.2 Incluir os dados públicos do anunciante no endpoint de detalhe; verificar com `xano_validate_xanoscript` e, após o envio pelo Xano CLI, por requisições sem token: nome e número só com autorização, nenhum dado de contato em `GET /vehicles` nem em veículo Vendido — endpoint alterado em `xano/` em 07/11/2026 e validado sem erros; cópia de segurança e prévia `--dry-run` feitas; enviado pelo usuário em 08/11/2026 (`seller.xs`, `vehicle.xs`, endpoint de detalhe; “Pushed 3 documents”); verificado sem token em 08/11/2026: `GET /vehicles` idêntico à cópia de 07/11 (3 veículos, sem dados de contato), `GET /vehicles/1` com `"seller": null` e sem `seller_id`, `GET /vehicles/999` com 404. Pendente verificar com anunciante real (depende de 2.3): número só com `contact_authorized` e nenhum contato em veículo Vendido
- [ ] 2.3 Cadastrar pelo painel do Xano anunciantes reais que autorizaram a exibição; verificar que nenhum contato fictício foi cadastrado — em 27/10/2026 o usuário informou que não há anunciantes reais autorizados; tarefa aguardando, sem cadastro de dados fictícios

## 3. Frontend

- [ ] 3.1 Trocar o “Tenho interesse” demonstrativo pelo bloco do anunciante e pelo link do WhatsApp; verificar com testes em `frontend/tests/` (com e sem autorização, sem anunciante, vendido) e no navegador — implementado em 07/11/2026: bloco “Anunciado por”, “Conversar no WhatsApp” (nova aba, `noopener noreferrer`) e “Contato não disponível”; `tests/test_contato.py` com dados simulados (com e sem autorização, sem anunciante, sem nome, vendido, números inválidos, mensagem sem endereço); 116 testes passam e `reflex compile` sem erros. Pendente a verificação no navegador (“Contato não disponível” nos 3 veículos após o envio; o botão só com anunciante real autorizado)

## 4. Verificação

- [ ] 4.1 Após o arquivamento de `detalhes-veiculo`, acrescentar o delta MODIFIED de “Interesse demonstrativo”; executar os testes, `reflex compile` e `openspec validate contato-vendedor --strict`; verificar que passam
