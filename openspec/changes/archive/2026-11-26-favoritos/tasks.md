# Tasks

> **Situação final (26/11/2026): concluída com ressalvas** (ver “Ressalvas” no fim), arquivada depois de `contas-acesso` e `anuncios-cliente`. O delta de `navegacao-site` mantém o cenário “Visitante aciona Anunciar veículo”. Leitura do Xano em 26/11/2026: a tabela `favorite` tem **3 registros** (`user_id` 3: veículos 13 e 6; `user_id` 4: veículo 3), criados depois dos testes de 24/11/2026 descritos abaixo; **preservar**.

> **Pós-merge (24/11/2026):** a PR #4 foi integrada à `main` (merge `32b5a68`), com os commits `4db828c`, `5bacd6d` e `43f3df1`. Tarefas completas; o arquivamento deve vir depois de `contas-acesso` e `anuncios-cliente` (mesmo requisito “Menu da conta” de `navegacao-site`). Este delta agora também modifica “Menu em tela estreita”, para que o texto final não mantenha “Favoritos” como “Em breve”.

> **Situação (24/11/2026):** implementação concluída (410 testes, `reflex compile --dry`, `xano_validate_xanoscript` com 37 arquivos válidos e `openspec validate favoritos --strict`); `favorite` e o grupo `Favoritos` publicados no Xano pelo usuário; teste manual no navegador com os Clientes A e B (favoritar, listar por conta, remover; listas e tabela vazias ao final). Registros não inspecionados no banco enquanto existiam; índice único e concorrência não testados (ver `design.md`). Nada enviado ao GitHub.

## 1. Backend local (sem envio ao Xano)
- [x] 1.1 Criar `xano/table/favorite.xs` (índice único `user_id`+`vehicle_id`); validar com `xano_validate_xanoscript`
- [x] 1.2 Criar o grupo `Favoritos` e os endpoints `GET /favoritos`, `POST /favoritos/{vehicle_id}`, `DELETE /favoritos/{vehicle_id}`; validar
- [x] 1.3 Teste estático dos `.xs` (`auth`, `enforce_role` primeiro, sem `user_id` na entrada, só veículos públicos)

## 2. Frontend
- [x] 2.1 `config.py`: `favoritos_api_url()`; `favoritos.py`: funções puras e `FavoritosState`
- [x] 2.2 Botão na página do veículo e página `/favoritos`; rota em `destino_seguro`; limpeza ao sair
- [x] 2.3 Menu: “Favoritos” como link; atualizar testes de menu
- [x] 2.4 Estilos em `styles.css`

## 3. Verificação
- [x] 3.1 Suíte completa, `reflex compile --dry` e `openspec validate favoritos --strict`
- [x] 3.2 Roteiro `docs/testes-favoritos.md` criado e executado parcialmente no navegador em 24/11/2026 (favoritar, listar por conta e remover); os cenários 3.1 a 3.5 e 4.1 e 4.2 do roteiro (API com token, Vendido e Rascunho) não foram executados

## Workflow follow-up
- Envio ao Xano, push e archive somente com autorização.

## Ressalvas: cenários não executados (26/11/2026)

**Motivo:** Decisão de escopo do usuário em 26/11/2026: nesta entrega não serão executados novos cadastros nem criados anúncios reais, o Chrome não será instalado e não haverá novas baterias manuais em múltiplos navegadores. Autorizada a revisão dos critérios adicionais de validação, preservados os requisitos funcionais. A conclusão desta Change **não** significa que os itens abaixo foram aprovados.

Origens usadas abaixo: **real** é teste do Claude em `localhost:3001` com o Xano, sem gravar dados; **usuário** é relato manual, sem capturas; **requisição** é chamada à API feita fora do navegador; **simulado** é a cópia isolada com backend fictício, que não equivale a teste real; **automatizado** são os testes Python com respostas simuladas ou leitura dos arquivos `.xs`.

| Item não executado no site real | O que existe |
| --- | --- |
| Visitante aciona “Favoritar” (retorno à ficha) | Automatizado |
| Favoritar duas vezes; índice único e envios simultâneos | Automatizado e leitura do `.xs` |
| `POST` em Rascunho ou identificador inexistente (404) | Automatizado e leitura do `.xs` |
| Veículo Vendido continua na lista; veículo que deixa de ser público some | Automatizado |
| Erro ao consultar favoritos | Automatizado |
| `/favoritos` a 375 px com sessão real | Simulado |
| Registros conferidos no banco enquanto o teste ocorria | Não feito |

Executados: favoritar, listar por conta, remover e isolamento entre contas (usuário, 24/11); redirecionamento de visitante em `/favoritos` (real, 26/11); 401 sem token (requisição).
