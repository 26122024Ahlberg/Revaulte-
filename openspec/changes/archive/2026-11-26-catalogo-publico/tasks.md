# Tasks

## 1. Preparação

- [x] 1.1 Confirmar com o Xano CLI que a pasta `xano/` está vinculada ao workspace correto e sem diferenças pendentes em relação ao remoto; verificar pela saída do comando de status/comparação do CLI (consultar `xano_cli_docs` no Xano Developer MCP para o comando exato)
- [x] 1.2 Consultar no Xano Developer MCP os tópicos `tables`, `apis` e `database` do XanoScript para a sintaxe de enum, valores padrão, `db.query` com filtro, ordenação e seleção de campos; verificar anotando no próprio PR/commit as construções confirmadas que serão usadas — **Concluída em 24/11/2026:** as construções de `vehicle.xs` (enum, valores padrão) e de `vehicles_GET.xs` (`db.query` com filtro, ordenação e `output`) estão publicadas no Xano, validadas por `xano_validate_xanoscript` (37 arquivos, 0 erros) e funcionam em execução. A consulta original ao MCP não deixou registro separado.
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

- 4.1 — **RETIRADA DO ESCOPO em 26/11/2026; NÃO EXECUTADA.** Decisão do usuário em 24/11/2026: não alterar veículos reais nem criar registros Vendido, Novo, sem versão ou sem imagem. Revisão formal em 26/11/2026. Texto original: Inserir pelo painel do Xano os registros de teste da decisão 9 do design (incluindo ao menos um Rascunho, um Vendido, um Modificado, um Novo, um sem versão e um sem imagem); verificar pela contagem de registros na tabela — **Atualização de 24/11/2026 (leitura):** há 7 registros (6 Disponíveis e 1 Rascunho, este sem versão, 5 modificados e 2 não modificados, todos `used`). **Faltam** registros Vendido e Novo; criá-los exigiria alterar dados, o que não foi autorizado. Decidir entre criar os registros temporariamente ou aceitar a cobertura por testes automáticos com ressalva. — **Decisão do usuário em 24/11/2026:** manter a cobertura automatizada com ressalva e não alterar veículos reais. A tarefa continua pendente porque o critério pede registros Vendido e Novo no Xano; só fechar com revisão formal de escopo.
- [x] 4.2 Verificar que a resposta do endpoint não contém o veículo em Rascunho: comparar os `id` devolvidos com os da tabela e confirmar que todo item tem `status` `available` ou `sold` — **Concluída em 24/11/2026 por leitura pública (sem alterar o Xano):** a tabela `vehicle` tem 7 registros (ids 1 a 7, o 7 em `draft`) e `GET /vehicles` devolve os ids 1 a 6, todos `available`; o Rascunho não aparece.
- [x] 4.3 Verificar que cada item da resposta contém somente os onze campos de catálogo, sem `created_at` nem outros campos — **Concluída em 24/11/2026 por leitura pública:** cada item de `GET /vehicles` tem exatamente os onze campos de catálogo (`brand`, `condition`, `cover_image_url`, `id`, `is_modified`, `mileage`, `model`, `price`, `status`, `version`, `year`), sem `created_at`, contato ou anunciante.
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
- [x] 8.2 Implementar em `CatalogState` a requisição assíncrona com tempo limite, disparada pelo `on_load` da página, substituindo os cartões de amostra provisórios da tarefa 7.3 (`CARTOES_AMOSTRA` em `state.py`, que devem ser removidos), e a alternância entre os estados carregando, lista, vazio e erro, com o botão “Tentar novamente”; verificar o estado de erro executando o app com `REVAULTE_CATALOG_API_URL` apontando para um endereço inválido, e a recuperação ao corrigir o endereço e tentar novamente — verificado em 13/11/2026: `CARTOES_AMOSTRA` não existe mais no código; a lista vem do Xano no `on_load` com tempo limite; no Safari (WebDriver), com uma cópia isolada do app apontando `REVAULTE_CATALOG_API_URL` para um servidor de teste em 503, `/estoque` exibe o estado de erro com “Tentar novamente”; quando o servidor de teste passa a repassar a resposta pública real de `GET /vehicles`, “Tentar novamente” carrega os 3 veículos e os filtros
- [x] 8.3 Implementar a preparação dos itens de exibição (título com versão quando houver, ano, quilometragem em km, preço em reais e condição “Novo” ou “Usado”) e a renderização com `rx.foreach`, sem `rx.html`; verificar a formatação com um teste Python das funções de preparação (incluindo veículo sem versão e preço `118900` → `R$ 118.900,00`) e comparando cada cartão com o registro correspondente no Xano
- [x] 8.4 Implementar os selos “Modificado” e “Vendido” e a aparência de indisponível do cartão vendido; verificar com os registros de teste que os selos aparecem só onde devem, inclusive no veículo vendido e modificado (verificado no Safari com dados simulados locais [SIMULADO], sem o Xano; a conferência com os registros reais depende da tarefa 4.1)
- [x] 8.5 Implementar a capa com validação do endereço (`http`/`https`) e troca para a imagem provisória quando ausente ou com falha ao carregar; verificar com o registro sem imagem e com um registro cujo endereço de imagem é inválido (verificado no Safari com dados simulados locais [SIMULADO], sem o Xano; a conferência com os registros reais depende da tarefa 4.1)

## 9. Verificação integrada

- [x] 9.1 Percorrer todos os cenários de `specs/catalogo-publico/spec.md` na página Reflex executada localmente com os dados de teste, registrando o resultado de cada cenário — catálogo funcionando confirmado pelo usuário no Safari (desktop) em 27/10/2026; pendente o registro cenário a cenário — **Cobertura automática de 24/11/2026 (não substitui o teste real):** os cenários de veículo Novo, Vendido e Modificado estão em `test_preparacao.py`, `test_pesquisa.py` e `test_detalhes.py`, e a regra “só Disponível e Vendido” está no teste estático de `vehicles_GET.xs`. Não há veículo Novo nem Vendido no Xano, então o selo e o cartão desses casos não foram vistos no navegador com dados reais. **Teste manual do Bloco 1 (visitante), relatado pelo usuário em 24/11/2026 em `localhost:3001`, sem capturas arquivadas:** catálogo (`/estoque`, `/usados`, `/modificados`) com pesquisa e filtros: OK; fichas `/veiculo/1`, `/2` e `/3`: OK; `/veiculo/7` e `/veiculo/999`: OK; modo offline com “Tentar novamente”: funcionamento confirmado; layout a 375 px: OK. Cobre os cenários de listagem, pesquisa e filtros com os 6 veículos Disponíveis. **Continua pendente:** cenários de veículo Vendido e Novo (não há registros) e o registro cenário a cenário da spec. — **Critério revisado em 26/11/2026:** registrar o resultado de cada cenário com os dados reais, sem alterar o Xano; ver a matriz “Resultado por cenário” abaixo, que identifica o que **não foi testado**.
- [x] 9.2 Inspecionar no navegador as requisições e as mensagens do WebSocket do Reflex e confirmar que nenhum dado do veículo em Rascunho chega ao navegador, que o navegador não acessa o Xano diretamente e que nenhuma credencial é enviada — **Sem evidência** (24/11/2026): chamadas diretas ao xano e mensagens do websocket **não** foram informados individualmente e não estão registrados como verificados. Continua pendente. — **Concluída em 26/11/2026** (verificação automatizada em 26/11/2026, em Edge sem janela, como visitante, em `localhost:3001` (roteiro e capturas temporários, não versionados)): em 51 carregamentos, o navegador não fez nenhuma requisição ao Xano; nas 836 mensagens WebSocket inspecionadas não apareceu dado do veículo em Rascunho, `Bearer`, token ou outra credencial, nem `seller_id` ou `contact_authorized`.
- 9.3 — **RETIRADA DO ESCOPO em 26/11/2026; NÃO EXECUTADA.** Exige alterar o preço de um veículo real (decisão do usuário em 24/11/2026). O reflexo de alterações do backend na página **não foi testado**. Texto original: Alterar o preço de um veículo no Xano, recarregar a página e confirmar que o novo valor é exibido
- [x] 9.4 Confirmar que a página não apresenta erros no console do navegador nem no terminal do `reflex run` e que os selos e mensagens são legíveis em tela estreita (até 560 px) — **Parcial (24/11/2026):** a 375 px o layout foi relatado como OK no Bloco 1 (relato do usuário). **Continua pendente** a ausência de erros no console e no terminal do `reflex run`, que não foi informada. — **Concluída em 26/11/2026 com ressalva.** Console sem erros e legibilidade a 560 px de `/modificados`, de uma ficha modificada, da pesquisa sem resultado e da imagem provisória (verificação automatizada em 26/11/2026, em Edge sem janela, como visitante, em `localhost:3001` (roteiro e capturas temporários, não versionados)). O terminal do `reflex run` foi conferido pelo usuário em **22/11/2026** (sem `ERROR`, `Exception` ou `Traceback` nas mensagens visíveis) e **não foi reinspecionado em 26/11/2026**. O selo “Vendido” a 560 px **não foi testado** com dados reais.
- [x] 9.5 Revisar o `git diff` e confirmar que, em relação ao commit da tarefa 1.4, há somente os arquivos previstos em `frontend/`, `frontend-html/`, `xano/table/vehicle.xs`, `xano/api/catalog/`, o `.gitignore` e os ajustes de documentação, sem credenciais, sem arquivos gerados pelo Reflex e sem alterações em `frontend-rascunho/` — **Atualização de 24/11/2026:** `frontend-rascunho/` e `frontend-html/` não mudam desde o commit `c4d7694` (MVP); o commit da tarefa 1.4 não existe como tal no histórico atual (consolidado em `c4d7694`); varredura de segredos e de arquivos como `.env`, chaves e tokens no repositório sem achados. **Conclusão da análise (24/11/2026):** `c4d7694` **não** substitui o commit da tarefa 1.4: ele é o MVP inteiro (75 arquivos, já com `state.py`, `vehicle.xs` e `xano/api/catalog/`), então não isola o que esta Change alterou. Por leitura, o objetivo da tarefa está atendido no estado atual: nenhum arquivo fora das pastas previstas em `c4d7694`; `frontend-html/` e `frontend-rascunho/` sem mudanças desde então; varredura de segredos na árvore sem achados. **Ressalva a registrar:** `frontend/reflex.lock/` (gerado pelo Reflex) está versionado desde `21aea86`. **Revisão de escopo aprovada pelo usuário em 24/11/2026:** a baseline isolada não é recuperável; o critério passa a ser a auditoria do estado atual descrita acima. Concluída com essa ressalva.
- [x] 9.6 Executar `openspec validate catalogo-publico --strict` e confirmar que não há erros — verificado em 21/10/2026 na auditoria do OpenSpec: 97 testes, `reflex compile` e `openspec validate --all --strict` passam; `git diff` sem alterações em `xano/` e `frontend-html/`

## Revisão de escopo e evidências (26/11/2026)

Revisão formal autorizada pelo usuário em 26/11/2026. Os requisitos da spec `catalogo-publico` não mudam. O que muda é o critério de verificação: os casos que dependiam de alterar dados reais saem do escopo e **não contam como testados**. “Automatizado” indica somente cobertura por testes Python com dados simulados; “simulado” indica navegador com dados simulados locais (tarefas 8.4 e 8.5).

### Resultado por cenário

| Cenário | Resultado |
| --- | --- |
| Visitante acessa o catálogo sem sessão | OK, navegador, 26/11 |
| Listagem pública consultada sem credenciais | OK, requisição sem token, 26/11 |
| Veículo publicado aparece no catálogo | OK, navegador, 26/11 (12 veículos) |
| Alteração no backend é refletida | **Não testado** (9.3 retirada) |
| Veículo em Rascunho não é devolvido | OK, requisição, 26/11 |
| Veículo em Rascunho não aparece na página | OK para Rascunho com Disponíveis, 26/11; convivência com Vendido **não testada** |
| Existem apenas veículos em Rascunho | Backend verificado (4.4, lista vazia); mensagem na página só automatizado |
| Resposta não expõe outros dados | OK, requisição, 26/11 |
| Veículo usado com todos os dados | OK, navegador, 26/11 |
| Veículo novo | **Não testado** com dados reais; automatizado |
| Veículo sem versão cadastrada | **Não testado** com dados reais; automatizado |
| Veículo modificado | OK, navegador, 26/11 |
| Veículo original | OK, navegador, 26/11 |
| Veículo novo e modificado | **Não testado** com dados reais; automatizado |
| Veículo vendido | **Não testado** com dados reais; simulado, 13/11 |
| Veículo disponível | OK, navegador, 26/11 |
| Veículo vendido e modificado | **Não testado** com dados reais; simulado, 13/11 |
| Veículo com imagem de capa | OK, navegador, 26/11 (com texto alternativo) |
| Veículo sem imagem de capa | **Não testado** com dados reais; simulado, 13/11 |
| Imagem de capa indisponível | OK, 26/11, bloqueando o servidor de imagens só no navegador de teste |
| Listagem em carregamento | OK, 13/11 e 22/11 (cópia isolada) |
| Catálogo vazio | **Não testado** no navegador; automatizado |
| Falha ao obter a listagem | OK, 13/11 e 22/11 (cópia isolada) e relato do usuário em 24/11 |
| Nova tentativa bem-sucedida | OK, 13/11 (cópia isolada) |

### Evidências de 22/11/2026 reconciliadas

Estavam somente em um `tasks.md` sem commit na worktree `Revaulte-contas-acesso`, que não foi alterada. Resumo do que aquele registro informa:

- teste manual do usuário no Opera, em `/estoque`: 56 requisições, nenhuma correspondendo ao filtro `xano`; 2 conexões WebSocket com status 101; console sem erros. A inspeção do conteúdo das mensagens ficou incompleta naquela data (feita em 26/11, tarefa 9.2);
- a 560 px: os três cartões então existentes legíveis, e a pesquisa sem resultado com mensagem e “Limpar filtros” legíveis;
- cópia isolada do app (portas 3010/8010, backend não roteável): “Carregando veículos…”, mensagem de erro e “Tentar novamente” legíveis a 560 px, por capturas do usuário;
- terminal do `reflex run`: compilação em 100%, sem `ERROR`, `Exception` ou `Traceback` nas mensagens visíveis; o histórico completo não foi inspecionado.
