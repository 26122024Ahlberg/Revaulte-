# Revaulte — Endpoints do Quick Start do Xano e logs de eventos

Registro da Change `contas-acesso` (tarefa 4.2, `design.md` decisões 6 e 10). O workspace nasceu com endpoints de exemplo do Quick Start do Xano. Três deles eram inseguros para a Revaulte e foram desativados; um quarto foi restringido. Este documento não contém tokens, hashes nem dados pessoais.

## Endpoints desativados

Cada arquivo mantém nome, verbo, grupo `Authentication`, `tags` e `guid`, e responde **404** sem consultar o banco, sem enviar e-mail, sem criar token ou sessão e sem registrar evento (`precondition (false)`). Foram enviados ao Xano em 19/11/2026. O frontend nunca os usou.

| Endpoint | Risco original | Situação |
| --- | --- | --- |
| `POST message/send_welcome_email` | Sem autenticação; aceitava qualquer `user_id`, enviava e-mail e gravava evento em nome de outro usuário | Desativado (404) |
| `GET reset/request-reset-link` | Recebia o e-mail na URL e gerava link de redefinição sem limitar tentativas; recuperação de senha está fora do escopo atual | Desativado (404) até haver uma Change de recuperação de senha |
| `POST reset/magic-link-login` | Mesmo fluxo; emitia token de sessão | Desativado (404) |

A função `Quick Start/generate_magic_link` continua no workspace, mas nenhum endpoint a chama; funções não são acessíveis externamente.

## Endpoint restringido: `GET logs/user/my_events`

- **Antes:** exigia token e devolvia ao próprio usuário todas as colunas dos seus eventos (incluindo `user_id` e `metadata`), sem ordem definida. Em 19/11/2026 poderia expor registros antigos com hash de senha, mas o `event_log` estava vazio e hoje todos os registros têm `metadata` igual a `{}` (inventário de 24/11/2026: 103 registros de `signup`, `login` e `get_auth_user`).
- **Correção local (24/11/2026, **ainda não publicada**):** continua filtrando por `$auth.id` e passa a devolver só `id`, `created_at` e `action`, do mais recente ao mais antigo, ainda como lista. O frontend não usa o endpoint.
- **Sem paginação:** a resposta continua um array para preservar o formato. Como cada abertura de página protegida gera um evento `get_auth_user`, a lista cresce; se o endpoint passar a ser usado, é preciso acrescentar limite.

## Regra para novos endpoints

Todo endpoint novo exige `auth = "user"` e `enforce_role`, exceto a lista abaixo. O teste `frontend/tests/test_pendencias_contas.py` varre `xano/api` e falha se aparecer endpoint sem `auth` fora dela.

| Sem `auth` permitido | Motivo |
| --- | --- |
| `auth/login`, `auth/signup` | Entrada de contas |
| `GET /vehicles`, `GET /vehicles/{id}` | Catálogo público (só Disponível e Vendido) |
| Os três do Quick Start desativados | Respondem 404 |

## Logs de eventos

- `login`, `signup`, `get_auth_user` e troca de senha gravam `metadata = {}`; nenhum endpoint grava o registro do usuário, senha, hash ou token (testado em `TestLogsSemDadosDeAutenticacao` e `TestMyEventsMinimo`).
- Nenhum registro do `event_log` foi apagado ou alterado nesta Change.

## Pendente de publicação

As alterações de `my_events` e da data de nascimento de `auth/signup` (ver `openspec/changes/contas-acesso/design.md`) existem somente nos arquivos locais.
