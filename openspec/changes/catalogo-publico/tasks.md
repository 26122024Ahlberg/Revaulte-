# Tasks

## 1. Preparação

- [ ] 1.1 Confirmar com o Xano CLI que a pasta `xano/` está vinculada ao workspace correto e sem diferenças pendentes em relação ao remoto; verificar pela saída do comando de status/comparação do CLI (consultar `xano_cli_docs` no Xano Developer MCP para o comando exato)
- [ ] 1.2 Consultar no Xano Developer MCP os tópicos `tables`, `apis` e `database` do XanoScript para a sintaxe de enum, valores padrão, `db.query` com filtro, ordenação e seleção de campos; verificar anotando no próprio PR/commit as construções confirmadas que serão usadas
- [x] 1.3 Atualizar em `docs/project-overview.md` o trecho “Workspace Xano”, que afirmava que o workspace ainda não foi configurado; verificar que o texto descreve o estado atual da pasta `xano/` (concluída na revisão da Change, antes da implementação)
- [ ] 1.4 Versionar o estado inicial de `xano/` e o `.gitignore` em um commit próprio, antes de criar os arquivos desta Change; verificar com `git status` que `xano/` não aparece mais como não rastreada e com `git diff --cached --name-only` que o commit contém somente arquivos `.xs`, o `.gitignore` e documentação, sem credenciais

## 2. Backend: tabela de veículos

- [ ] 2.1 Criar `xano/table/vehicle.xs` com os campos e padrões definidos na decisão 1 do design (`status` padrão `draft`, `is_modified` padrão `false`) e índice primário; verificar com `xano_validate_xanoscript` sem erros
- [ ] 2.2 Enviar a tabela ao workspace com o Xano CLI; verificar no painel do Xano que a tabela `vehicle` existe com todos os campos e que `user` e `event_log` permanecem inalteradas

## 3. Backend: endpoint público do catálogo

- [ ] 3.1 Criar o grupo de API `Catalog` em `xano/api/catalog/catalog.xs` com `canonical` específico do projeto; verificar com `xano_validate_xanoscript` sem erros
- [ ] 3.2 Criar `xano/api/catalog/vehicles_GET.xs` sem `auth`, filtrando `status` em `available` ou `sold`, ordenando por `created_at` decrescente e devolvendo somente os campos de catálogo; verificar com `xano_validate_xanoscript` sem erros
- [ ] 3.3 Enviar o grupo e o endpoint ao workspace com o Xano CLI; verificar que uma requisição `GET` sem token ao endereço público responde 200 com uma lista JSON

## 4. Dados de teste e verificação do backend

- [ ] 4.1 Inserir pelo painel do Xano os registros de teste da decisão 9 do design (incluindo ao menos um Rascunho, um Vendido, um Modificado, um Novo, um sem versão e um sem imagem); verificar pela contagem de registros na tabela
- [ ] 4.2 Verificar que a resposta do endpoint não contém o veículo em Rascunho: comparar os `id` devolvidos com os da tabela e confirmar que todo item tem `status` `available` ou `sold`
- [ ] 4.3 Verificar que cada item da resposta contém somente os onze campos de catálogo, sem `created_at` nem outros campos
- [ ] 4.4 Alterar temporariamente todos os registros para Rascunho (ou usar uma tabela vazia) e verificar que o endpoint responde 200 com lista vazia; restaurar os estados em seguida

## 5. Frontend: estrutura e estilos

- [ ] 5.1 Criar a estrutura `frontend/` (`catalogo.html`, `css/styles.css`, `js/config.js`, `js/catalogo.js`, `img/placeholder.svg`); verificar que `git status` não mostra nenhuma alteração em `frontend-rascunho/`
- [ ] 5.2 Escrever `catalogo.html` com topo, título da página, região de estados (carregando, lista, vazio, erro) e rodapé, sem veículos fixos e sem links para páginas inexistentes; verificar abrindo a página e conferindo que o HTML não contém nenhum cartão de veículo
- [ ] 5.3 Escrever `css/styles.css` reaproveitando do rascunho variáveis de cor, tipografia, botões, topo, rodapé e `.card`, e acrescentando os estilos dos selos, do cartão vendido e das mensagens de estado; verificar visualmente a grade em 4, 2 e 1 colunas ao redimensionar a janela
- [ ] 5.4 Criar `img/placeholder.svg` como imagem provisória; verificar que ela é exibida ao ser aberta diretamente no navegador

## 6. Frontend: integração com o Xano

- [ ] 6.1 Definir em `js/config.js` o endereço base do grupo de API `Catalog`; verificar que o arquivo não contém token, chave ou credencial
- [ ] 6.2 Implementar em `js/catalogo.js` a requisição `fetch` da listagem e a alternância entre os estados carregando, lista, vazio e erro, com o botão “Tentar novamente”; verificar o estado de erro apontando temporariamente `config.js` para um endereço inválido e a recuperação ao corrigir e tentar novamente
- [ ] 6.3 Implementar a montagem dos cartões com `createElement` e `textContent`, exibindo marca, modelo, versão quando houver, ano, quilometragem, preço em reais e condição “Novo” ou “Usado”; verificar comparando cada cartão com o registro correspondente no Xano
- [ ] 6.4 Implementar os selos “Modificado” e “Vendido” e a aparência de indisponível do cartão vendido; verificar com os registros de teste que os selos aparecem só onde devem, inclusive no veículo vendido e modificado
- [ ] 6.5 Implementar a imagem de capa com validação do endereço e troca para a imagem provisória quando ausente ou com falha; verificar com o registro sem imagem e com um registro cujo endereço de imagem é inválido
- [ ] 6.6 Verificar que a requisição funciona com a página servida por um servidor HTTP local, sem erro de CORS no console do navegador; ajustar a configuração de CORS do grupo de API no Xano se necessário

## 7. Verificação integrada

- [ ] 7.1 Percorrer todos os cenários de `specs/catalogo-publico/spec.md` com a página servida localmente e os dados de teste, registrando o resultado de cada cenário
- [ ] 7.2 Inspecionar a aba de rede do navegador e confirmar que nenhum dado do veículo em Rascunho é recebido e que nenhuma requisição envia token de autenticação
- [ ] 7.3 Alterar o preço de um veículo no Xano, recarregar a página e confirmar que o novo valor é exibido
- [ ] 7.4 Confirmar que a página não apresenta erros no console e que os selos e mensagens são legíveis em tela estreita (até 560 px)
- [ ] 7.5 Revisar o `git diff` e confirmar que, em relação ao commit da tarefa 1.4, há somente os arquivos previstos em `frontend/`, `xano/table/vehicle.xs` e `xano/api/catalog/`, sem credenciais e sem alterações em `frontend-rascunho/`
- [ ] 7.6 Executar `openspec validate catalogo-publico --strict` e confirmar que não há erros
