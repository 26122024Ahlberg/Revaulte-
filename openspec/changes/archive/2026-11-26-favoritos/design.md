# Design

## Decisões

1. **Persistência no Xano, por conta.** Favorito é dado do Cliente e deve acompanhá-lo entre navegadores; por isso a tabela `favorite` (`user_id`, `vehicle_id`, `created_at`) tem índice único composto (`user_id`, `vehicle_id`). Não usar armazenamento local do navegador.
2. **Backend devolve só ids.** `GET /favoritos` retorna `[{vehicle_id, created_at}]` da conta do token, mais recentes primeiro. A página reaproveita `GET /vehicles` (catálogo público, que já filtra Rascunho) e exibe somente os veículos cujo id está na lista. Assim nenhum dado de veículo não público vaza e não há `join` novo.
3. **Idempotência.** `POST /favoritos/{id}` consulta antes de gravar; repetir não duplica e responde 200. `DELETE` de favorito inexistente responde 200. O índice único cobre corridas.
4. **Só veículo público.** `POST` exige veículo existente com `status` `available` ou `sold`; caso contrário 404 (`not_found`), igual para inexistente e Rascunho.
5. **Autorização.** `auth = "user"` + `enforce_role` (`member`) antes de qualquer consulta; 401 sem token; 403 sem cargo. Nenhum endpoint aceita `user_id` na entrada.
6. **Frontend.** `FavoritosState` (ids favoritados, situação), reutilizando `chamar_xano`, `AuthState._exigir` e o padrão de `anuncios.py`. Na página do veículo, com sessão, o botão consulta `GET /favoritos` ao abrir e alterna por `POST`/`DELETE`; fica desabilitado durante a requisição; erro mostra mensagem própria, sem texto cru do backend. `/favoritos` exige login (`/entrar?proximo=/favoritos`).
7. **Limite do plano Xano** (10 req/20 s): a página do veículo logado faz uma requisição extra; `/favoritos` faz `auth/me`, `GET /favoritos` e `GET /vehicles`.
8. **Saída da conta** limpa o estado de favoritos.

## Plano de migração

Somente arquivos locais nesta fase. O envio ao Xano depende de autorização: cópia de segurança antes, prévia `--dry-run` com `-i "table/favorite.xs" -i "api/favoritos/**"`, sem `--sync`, `--delete` nem `--force`. Reversão: remover o grupo `Favoritos` e a tabela `favorite` pelo painel (nenhum dado existente é alterado).

## Verificação

Testes unitários de funções e estados (respostas simuladas), teste estático dos `.xs`, `xano_validate_xanoscript`, `reflex compile`, e roteiro manual em `docs/testes-favoritos.md` com o Xano real após o envio.

## Estado dos registros (26/11/2026)

Leitura do banco em 26/11/2026 (`pull --records`): `favorite` tem **3 registros** (`user_id` 3: veículos 13 e 6; `user_id` 4: veículo 3), criados depois da verificação de 24/11/2026 descrita abaixo. Eles **devem ser preservados**: a limpeza prevista no roteiro de testes não se aplica a eles. A mesma leitura não permite afirmar como foram criados.

## Verificação real (24/11/2026)

**Publicação (leitura no Xano, sem alterar nada):** tabela `favorite` com índice único composto (`user_id`, `vehicle_id`) e índice comum em `vehicle_id`, três endpoints e o grupo `Favoritos`; prévia `--dry-run` com “No changes to push”; sem token, `GET`, `POST` e `DELETE` respondem 401, e token inválido responde 401.

**Teste manual no navegador (Clientes A e B, contas 3 e 5), conforme relato e capturas de tela da equipe:**

- favoritar na página do veículo e listar em `/favoritos`, com listas separadas por conta (A viu Opala e Chevette; B viu Gol GTI Turbo);
- depois de remover os favoritos pela página, as listas de A e de B ficaram vazias;
- o Xano mostrou `favorite` com 0 registros ao final.

**Limites desta evidência:** os registros de `favorite` **não foram inspecionados no banco enquanto existiam** (as leituras do banco feitas por `pull --records` mostraram a tabela já vazia). Portanto não há prova direta, no banco, dos pares `user_id` + `vehicle_id`, da ausência de duplicatas nem do veículo 7 (draft) fora dos favoritos; esses pontos têm cobertura apenas nos testes automáticos (simulados) e na revisão do código. **O índice único não foi testado em execução nem em concorrência.**

**Integridade (leitura, `pull --records`):** `vehicle` com 7 registros (ids 1 a 6 `available`, 7 `draft`), `seller` (2), `seller_account` (1), `user` (3: ids 3 e 5 `member`, 4 `admin`) e `vehicle_modification` (0) idênticos ao backup anterior ao teste; código publicado idêntico; o `event_log` só recebeu eventos de `login` e `get_auth_user`.
