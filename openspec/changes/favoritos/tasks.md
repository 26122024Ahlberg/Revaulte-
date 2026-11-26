# Tasks

> **Situação (26/11/2026): tarefas completas, ABERTA por dependência.** Arquivar depois de `contas-acesso` e `anuncios-cliente`. O delta de `navegacao-site` foi corrigido para manter o cenário “Visitante aciona Anunciar veículo”. Conferido na segunda rodada: cenários preservados na sequência dos três deltas, `Purpose` preenchido e `openspec validate favoritos --strict` válido. No arquivamento, o texto de “Menu da conta” (acima de 500 caracteres) voltará a gerar o aviso do modo estrito e deve ser condensado. Leitura do Xano em 26/11/2026: a tabela `favorite` tem **3 registros** (`user_id` 3: veículos 13 e 6; `user_id` 4: veículo 3), criados depois dos testes de 24/11/2026 descritos abaixo; **preservar**.

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
