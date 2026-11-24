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
