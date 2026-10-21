# Tasks

## 1. Preparação

- [x] 1.1 Confirmar com o Xano CLI que a pasta `xano/` está vinculada ao workspace correto e sem diferenças pendentes em relação ao remoto; verificar pela saída do comando de status/comparação do CLI (consultar `xano_cli_docs` no Xano Developer MCP para o comando exato)
- [ ] 1.2 Consultar no Xano Developer MCP os tópicos `tables`, `apis` e `database` do XanoScript para a sintaxe de enum, valores padrão, `db.query` com filtro, ordenação e seleção de campos; verificar anotando no próprio PR/commit as construções confirmadas que serão usadas
- [x] 1.3 Atualizar em `docs/project-overview.md` o trecho “Workspace Xano”, que afirmava que o workspace ainda não foi configurado; verificar que o texto descreve o estado atual da pasta `xano/` (concluída na revisão da Change, antes da implementação)
- [x] 1.4 Versionar o estado inicial de `xano/` e o `.gitignore` em um commit próprio, antes de criar os arquivos desta Change; verificar com `git status` que `xano/` não aparece mais como não rastreada e com `git diff --cached --name-only` que o commit contém somente arquivos `.xs`, o `.gitignore` e documentação, sem credenciais

## 2. Backend: tabela de veículos

- [x] 2.1 Criar `xano/table/vehicle.xs` com os campos e padrões definidos na decisão 1 do design (`status` padrão `draft`, `is_modified` padrão `false`) e índice primário; verificar com `xano_validate_xanoscript` sem erros
- [x] 2.2 Enviar a tabela ao workspace com o Xano CLI; verificar no painel do Xano que a tabela `vehicle` existe com todos os campos e que `user` e `event_log` permanecem inalteradas

## 3. Backend: endpoint público do catálogo

- [x] 3.1 Criar o grupo de API `Catalog` em `xano/api/catalog/catalog.xs` com `canonical` específico do projeto; verificar com `xano_validate_xanoscript` sem erros
- [x] 3.2 Criar `xano/api/catalog/vehicles_GET.xs` sem `auth`, filtrando `status` em `available` ou `sold`, ordenando por `created_at` decrescente e devolvendo somente os campos de catálogo; verificar com `xano_validate_xanoscript` sem erros
- [x] 3.3 Enviar o grupo e o endpoint ao workspace com o Xano CLI; verificar que uma requisição `GET` sem token ao endereço público responde 200 com uma lista JSON

## 4. Dados de teste e verificação do backend

- [ ] 4.1 Inserir pelo painel do Xano os registros de teste da decisão 9 do design (incluindo ao menos um Rascunho, um Vendido, um Modificado, um Novo, um sem versão e um sem imagem); verificar pela contagem de registros na tabela
- [ ] 4.2 Verificar que a resposta do endpoint não contém o veículo em Rascunho: comparar os `id` devolvidos com os da tabela e confirmar que todo item tem `status` `available` ou `sold`
- [ ] 4.3 Verificar que cada item da resposta contém somente os onze campos de catálogo, sem `created_at` nem outros campos
- [x] 4.4 Alterar temporariamente todos os registros para Rascunho (ou usar uma tabela vazia) e verificar que o endpoint responde 200 com lista vazia; restaurar os estados em seguida

## 5. Versão HTML de referência

- [x] 5.1 Criar em `frontend/` a versão em HTML, CSS e JavaScript puro da página de catálogo (`catalogo.html`, `css/styles.css`, `js/config.js`, `js/catalogo.js`, `img/placeholder.svg`) integrada ao endpoint público (concluída antes da determinação de usar Reflex; verificado: HTML sem cartões fixos, `config.js` sem credenciais, `frontend-rascunho/` intacto e, no navegador, marca Revaulte e veículo cadastrado exibidos). Deixa de ser o frontend oficial e passa a ser referência (decisão 11 do design)
- [x] 5.2 Mover a pasta `frontend/` para `frontend-html/` sem alterar nenhum arquivo; verificar com `diff -r` contra uma cópia prévia que o conteúdo é idêntico e que nada foi apagado

## 6. Ambiente Reflex

- [x] 6.1 Instalar Python 3.11 ou superior (proposto: Python 3.12 pelo Homebrew), somente após aprovação do usuário; verificar com `python3.12 --version`
- [x] 6.2 Criar o app Reflex `revaulte` em `frontend/` com ambiente virtual em `frontend/.venv`, `requirements.txt` com a versão do Reflex fixada, `rxconfig.py`, a estrutura da decisão 6 do design e um `README.md` com os comandos de instalação e execução; acrescentar `.web/`, `.states/`, `.venv/` e `__pycache__/` ao `.gitignore`; verificar que `reflex run` sobe sem erros e que `git status` não lista arquivos gerados
- [x] 6.3 Confirmar com um teste mínimo se uma imagem (`rx.el.img` ou `rx.image`) com endereço inválido dispara um evento de erro tratável no estado; se não houver suporte, pausar e propor alternativa antes de seguir, sem reduzir o requisito da imagem provisória

## 7. Frontend Reflex: estrutura e identidade visual

- [x] 7.1 Copiar `frontend-html/img/placeholder.svg` para `frontend/assets/placeholder.svg` e portar `frontend-html/css/styles.css` para `frontend/assets/styles.css`, carregando-o com as fontes Google em `rx.App(stylesheets=[...])` e aparência escura; verificar que `/placeholder.svg` e `/styles.css` são servidos pelo app
- [x] 7.2 Implementar em `components.py` o topo (marca Revaulte e item “Catálogo” como página atual), o título da página, a região de estados e o rodapé, e em `revaulte.py` a página `/catalogo` com título “Catálogo | Revaulte” e o redirecionamento de `/`; verificar no navegador, lado a lado com `frontend-html/`, que fundo, fontes, cores, topo e rodapé correspondem, que não há links para páginas inexistentes e que o nome GhostPay não aparece
- [x] 7.3 Aplicar os estilos da grade de cartões, dos selos, do cartão vendido e das mensagens de estado; verificar visualmente a grade em 4, 2 e 1 colunas ao redimensionar a janela

## 8. Frontend Reflex: integração com o Xano

- [x] 8.1 Definir em `revaulte/config.py` o endereço base do grupo `Catalog`, lido de `REVAULTE_CATALOG_API_URL` com o endereço público atual como padrão; verificar que o arquivo não contém token, chave ou credencial
- [ ] 8.2 Implementar em `CatalogState` a requisição assíncrona com tempo limite, disparada pelo `on_load` da página, substituindo os cartões de amostra provisórios da tarefa 7.3 (`CARTOES_AMOSTRA` em `state.py`, que devem ser removidos), e a alternância entre os estados carregando, lista, vazio e erro, com o botão “Tentar novamente”; verificar o estado de erro executando o app com `REVAULTE_CATALOG_API_URL` apontando para um endereço inválido, e a recuperação ao corrigir o endereço e tentar novamente
- [x] 8.3 Implementar a preparação dos itens de exibição (título com versão quando houver, ano, quilometragem em km, preço em reais e condição “Novo” ou “Usado”) e a renderização com `rx.foreach`, sem `rx.html`; verificar a formatação com um teste Python das funções de preparação (incluindo veículo sem versão e preço `118900` → `R$ 118.900,00`) e comparando cada cartão com o registro correspondente no Xano
- [x] 8.4 Implementar os selos “Modificado” e “Vendido” e a aparência de indisponível do cartão vendido; verificar com os registros de teste que os selos aparecem só onde devem, inclusive no veículo vendido e modificado (verificado no Safari com dados simulados locais [SIMULADO], sem o Xano; a conferência com os registros reais depende da tarefa 4.1)
- [x] 8.5 Implementar a capa com validação do endereço (`http`/`https`) e troca para a imagem provisória quando ausente ou com falha ao carregar; verificar com o registro sem imagem e com um registro cujo endereço de imagem é inválido (verificado no Safari com dados simulados locais [SIMULADO], sem o Xano; a conferência com os registros reais depende da tarefa 4.1)

## 9. Verificação integrada

- [ ] 9.1 Percorrer todos os cenários de `specs/catalogo-publico/spec.md` na página Reflex executada localmente com os dados de teste, registrando o resultado de cada cenário
- [ ] 9.2 Inspecionar no navegador as requisições e as mensagens do WebSocket do Reflex e confirmar que nenhum dado do veículo em Rascunho chega ao navegador, que o navegador não acessa o Xano diretamente e que nenhuma credencial é enviada
- [ ] 9.3 Alterar o preço de um veículo no Xano, recarregar a página e confirmar que o novo valor é exibido
- [ ] 9.4 Confirmar que a página não apresenta erros no console do navegador nem no terminal do `reflex run` e que os selos e mensagens são legíveis em tela estreita (até 560 px)
- [ ] 9.5 Revisar o `git diff` e confirmar que, em relação ao commit da tarefa 1.4, há somente os arquivos previstos em `frontend/`, `frontend-html/`, `xano/table/vehicle.xs`, `xano/api/catalog/`, o `.gitignore` e os ajustes de documentação, sem credenciais, sem arquivos gerados pelo Reflex e sem alterações em `frontend-rascunho/`
- [ ] 9.6 Executar `openspec validate catalogo-publico --strict` e confirmar que não há erros
