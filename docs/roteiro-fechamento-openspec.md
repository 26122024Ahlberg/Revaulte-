# Revaulte — Roteiro curto de fechamento do OpenSpec (até 27/11/2026)

Um único percurso pelo navegador, com quatro perfis em sequência. Cobre `catalogo-publico`, `contas-acesso`, `detalhes-veiculo`, `contato-vendedor` e `anuncios-cliente`. `favoritos` já está completa; `chat-interno` fica aberta.

## Regras

- Site em `http://localhost:3001/`, com **Console e Rede abertos** o tempo todo. Uma ação por vez (limite de 10 requisições a cada 20 s).
- **Não** criar, editar ou excluir veículo, conta, anúncio ou favorito. **Não** enviar o formulário de anúncio com dados válidos. Reaproveitar o anúncio 7 e as contas A (ID 3) e B (ID 5).
- Responder cada passo com **OK** ou o que apareceu. Sem senhas nem tokens em arquivos.

> **Atualização (26/11/2026):** o percurso e os registros abaixo são históricos. A situação atual das Changes está em “Fechamento (26/11/2026)”, no fim deste documento.

## Percurso

| # | Perfil | Ação | Esperado | Fecha |
| --- | --- | --- | --- | --- |
| 1 | Visitante (janela anônima) | `/estoque`, `/usados`, `/modificados`; pesquisar e filtrar | 6 veículos; pesquisa e filtros funcionam | catálogo 9.1, 9.2 |
| 2 | Visitante | `/veiculo/1`, `/veiculo/2` e `/veiculo/3` | 1: “Anunciado por” e “Conversar no WhatsApp” (nova aba); 2 e 3: “Contato não disponível”, “Não informado” onde faltar dado; 3 mostra modificações | detalhes 1.3/3.1, contato 3.1 |
| 3 | Visitante | `/veiculo/7` e `/veiculo/999` | “Veículo não encontrado”, igual nos dois | detalhes 1.3 |
| 4 | Visitante | Rede em **offline** → abrir `/veiculo/1` → voltar online → “Tentar novamente” | Mensagem de erro e depois a ficha | detalhes 1.3 |
| 5 | Visitante | `/conta`, `/admin`, `/anunciar`, `/meus-anuncios`, `/favoritos` | Cada uma vai a `/entrar?proximo=…`. Repetir **uma delas no Opera** e anotar se `?proximo=` aparece | contas 3.2, 3.7 |
| 6 | Visitante | `/cadastro` vazio, com CPF inválido e com senha fraca; `/entrar` com senha errada | Mensagens claras; nenhuma conta criada; “E-mail ou senha incorretos.” | contas 3.2 |
| 7 | Cliente A | Entrar; ☰; `/conta`; `/admin` | Menu com Minha conta, Anunciar, Meus anúncios, Favoritos e Sair; sem CPF, telefone e endereço; `/admin` = “Acesso restrito” | contas 3.3, 3.4 |
| 8 | Cliente A | `/meus-anuncios` → “Ver detalhes” do anúncio 7; `/veiculo/7` | Lista com o 7 em “Rascunho”; ficha sem editar nem excluir e sem link público; `/veiculo/7` continua 404 | anúncios 8.2 |
| 9 | Cliente A | `/anunciar`: enviar **vazio** e com preço/ano inválidos (sem envio válido) | Mensagem do primeiro campo inválido; nada é enviado | anúncios 8.2 |
| 10 | Cliente A | Sair | Volta à Home; `/conta` leva ao login | contas 3.3 |
| 11 | Cliente B | Entrar; `/meus-anuncios`; depois `/meus-anuncios/7`, `/meus-anuncios/1`, `/meus-anuncios/999` | Lista vazia com “Anunciar veículo”; os três mostram o mesmo “Anúncio não encontrado” | anúncios 8.2 |
| 12 | Administrador | Entrar; ☰; `/admin` | “Painel administrativo” no menu; lista de usuários (ID, data, nome, e-mail, perfil), sem ações de edição | contas 1.8, 3.3 |
| 13 | Qualquer | **375 px** (modo dispositivo): ☰ de visitante, de Cliente e de Administrador; `/estoque`, `/veiculo/1`, `/entrar`, `/cadastro`, `/meus-anuncios`, `/admin` | Sem rolagem horizontal; selos e mensagens legíveis | contas 3.4, 3.5; catálogo 9.4 |
| 14 | Todos | Console e Rede ao longo do percurso | Sem erros; o navegador não chama o Xano; nada do veículo 7 aparece para visitante | catálogo 9.2, 9.4; detalhes 4.1 |

## Registro de execução — Bloco 1 (visitante), 24/11/2026

Testes manuais **relatados pelo usuário** em `localhost:3001`, sem capturas arquivadas e sem dados pessoais. As cinco verificações foram marcadas como concluídas.

| Resultado informado | Passos do percurso | Resultado |
| --- | --- | --- |
| Catálogo (`/estoque`, `/usados`, `/modificados`), pesquisa e filtros | 1 | **OK** relatado |
| Fichas `/veiculo/1`, `/2` e `/3` | 2 | **OK** relatado |
| `/veiculo/7` e `/veiculo/999` | 3 | **OK** relatado |
| Modo offline e “Tentar novamente” | 4 | Funcionamento confirmado expressamente |
| Layout a 375 px | 13 (parte do visitante) | **OK** relatado |

**Não informado, portanto não registrado como verificado:** console sem erros, ausência de chamadas diretas ao Xano e inspeção do WebSocket (passos 14 e 7 do percurso de 14 linhas). **Não executados:** cenários de veículo Novo e Vendido e modificações por área com registros.

## Registro de execução — Bloco 2 (autenticação e contas), 24/11/2026

Executado pelo usuário em `localhost:3001`; resultados informados, sem capturas arquivadas e sem dados pessoais.

| Resultado informado | Passos do percurso | Tarefas de `contas-acesso` |
| --- | --- | --- |
| Visitante e redirecionamento das rotas protegidas: **OK** | 5 | 3.3 |
| Validação de cadastro e login inválidos: **OK** | 6 | 3.2 (parcial) |
| Cliente A: menu, Minha conta e restrição administrativa: **OK** | 7 | 3.3, 3.4 (parcial) |
| Logout e proteção após sair: **OK** | 10 | 3.3 |
| Administrador: menu e painel de usuários: **OK** | 12 | 1.8, 3.3 |
| Layout a 375 px e verificação no Opera: **OK** | 13 e Opera do passo 5 | 3.5, 3.7 (parcial), 3.4 (parcial) |

Concluídas por esse registro: 1.8, 3.3 e 3.5. Continuam abertas: 3.2 (cadastro válido, e-mail ou CPF já cadastrados, `aria-live` e botão desabilitado), 3.4 (menus a 375 px confirmados um a um), 3.7 (falta o Chrome) e 4.3. Os passos 1 a 4 (catálogo, detalhes e contato) e 8, 9 e 11 (anúncios) não fazem parte do Bloco 2 e seguem pendentes.

## Registro de execução — Bloco 3 (anúncios de Clientes), 24/11/2026

Testes manuais **relatados pelo usuário** em `localhost:3001`, sem capturas arquivadas e sem dados pessoais. Nenhum anúncio foi criado.

| # | Resultado informado | Passo do percurso | Resultado |
| --- | --- | --- | --- |
| 1 | Cliente A abre `/meus-anuncios` e vê o anúncio 7 como Rascunho | 8 | **OK** |
| 2 | Cliente A abre a ficha privada do 7, sem editar nem excluir; `/veiculo/7` segue indisponível ao público | 8 | **OK** |
| 3 | `/anunciar` rejeita envio vazio e preço e ano inválidos, sem envio válido | 9 | **OK** |
| 4 | Cliente B abre `/meus-anuncios` e não vê anúncios da conta A | 11 | **OK** |
| 5 | Cliente B abre `/meus-anuncios/7`, `/meus-anuncios/1` e `/meus-anuncios/999`: o mesmo “Anúncio não encontrado” | 11 | **OK** |

**Não testado no navegador:** envio válido pelo formulário (o anúncio 7 foi criado por API em 23/11/2026), redirecionamento com aviso, segundo anúncio, nome de exibição só no primeiro anúncio e 375 px das páginas de anúncios. A tarefa 3.5 (limpeza do anúncio 7 e da conta B) continua pendente, só depois do vídeo.

## Decisões e resultados (24/11/2026)

| Tarefa | Situação | Falta |
| --- | --- | --- |
| catálogo 4.1, 9.1 (Novo/Vendido), 9.3; detalhes 2.4, 4.1; contato 2.2 | Cobertura **automatizada com ressalva**: não existe veículo Novo nem Vendido no Xano e os veículos reais não serão alterados | Continuam pendentes; só fecham com revisão formal de escopo, nunca marcadas como testadas |
| catálogo 9.5 | **Concluída com ressalva**: a baseline isolada não é recuperável; vale a auditoria do estado atual (nenhum arquivo fora do previsto, `frontend-html` e `frontend-rascunho` intactos, sem segredos; `reflex.lock` versionado). `c4d7694` **não** é a baseline original | Nada |
| contas 1.6 | Conta sem cargo (403) com ressalva de cobertura automatizada; nenhuma conta será criada | Continua pendente |
| contas 2.3 | `my_events` reduzido a `id`, `created_at` e `action`, só da própria conta; **publicado e verificado em execução em 24/11/2026** (401 sem token; 200 com 58 eventos, só `id`, `created_at` e `action`) | Nada |
| contas 2.4 | **Concluída**: teste global de endpoints sem `auth` | Nada |
| contas 2.13 | Backend alinhado ao frontend (data de hoje em Brasília), com testes de datas-limite; **publicado e verificado em execução em 24/11/2026** (hoje → `invalid_birth_date`; ontem passa na data) | Nada |
| contas 3.6 | **Concluída**: mensagem própria para HTTP 429 em login e cadastro | Nada (429 real não provocado) |
| contas 4.2 | **Concluída**: `docs/seguranca-endpoints-quick-start.md` | Nada |
| anúncios 8.2 | O anúncio 7 foi criado **por API, não pelo navegador**; não será criado outro | Continua pendente (ou revisão formal de escopo) |
| anúncios 3.5 | Limpeza do anúncio 7 e da conta B | Só depois do vídeo, com autorização |
| contato 4.1 | Delta de “Interesse demonstrativo” | Só depois de arquivar `detalhes-veiculo` |

## Ordem de arquivamento planejada em 24/11/2026

1. `catalogo-publico`.
2. `contas-acesso` → `anuncios-cliente` → `favoritos` (o último deve ser `favoritos`, que finaliza “Menu da conta” e “Menu em tela estreita”).
3. `detalhes-veiculo` → `contato-vendedor`.
4. `chat-interno` permanece aberta.

Cada arquivamento: `openspec validate <change> --strict` antes e `openspec validate --all` depois. Uma única PR `docs/openspec-pos-merge` → `main` (merge commit), com o commit de checklists, o registro dos resultados deste percurso e um commit por arquivamento. Sem código nem Xano na PR.

## Fechamento (26/11/2026)

Verificação automatizada em Edge sem janela, como visitante, em `localhost:3001` (roteiro e capturas temporários, não versionados), além de leituras no Xano e requisições sem token. Nenhum dado, imagem ou código publicado foi alterado.

| Change | Situação | Motivo |
| --- | --- | --- |
| `destaques-editoriais` | Arquivada | Tarefas concluídas |
| `catalogo-publico` | Arquivada | Critérios revisados; casos não testados registrados |
| `detalhes-veiculo` | Arquivada | Critérios revisados; casos não testados registrados |
| `contato-vendedor` | Arquivada | Critérios revisados e delta de `detalhes-veiculo` aplicado |
| `contas-acesso` | **Aberta** | 3.2, 3.4, 3.7 e 4.3: cadastro válido e e-mail ou CPF repetidos pelo formulário, menus de Cliente e Administrador a 375 px, sessão expirada, falha na lista de usuários e Chrome |
| `anuncios-cliente` | **Aberta** | 8.2: páginas de anúncios com sessão (375 px, console, rede e nome de exibição); depende de `contas-acesso` |
| `favoritos` | **Aberta** | Tarefas completas; depende de `contas-acesso` e `anuncios-cliente` |
| `chat-interno` | **Cancelada** | Contato somente pelo WhatsApp; ver `openspec/changes-canceladas/chat-interno/` |

Ordem para o que falta: `contas-acesso` → `anuncios-cliente` → `favoritos`. Enquanto isso, `openspec/specs/navegacao-site` ainda descreve o menu anterior, com os itens “Em breve”; o menu atual está descrito no delta de `favoritos`.

A integração `docs/openspec-pos-merge` → `main` leva também código do frontend, testes e dois arquivos `.xs` já publicados (commits `0d32eb5` e `0d157a1`); a integração em si não envia nada ao Xano. Isso substitui a observação “Sem código nem Xano na PR” acima.

