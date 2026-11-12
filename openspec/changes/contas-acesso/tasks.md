# Tasks

> **Situação (12/11/2026): EM DESENVOLVIMENTO na branch `feat/contas-acesso`.** Depende do envio das alterações ao Xano, ainda **não publicadas** (aguardam cópia de segurança, prévia `--dry-run` e autorização do usuário). Não fazer merge na `main` antes disso e antes de concluir as páginas do frontend.

## 1. Backend Xano (arquivos locais; envio somente com autorização)

- [x] 1.1 Acrescentar `cpf`, `phone`, `birth_date` e `address` (sensíveis, opcionais na tabela) e índice em `cpf` em `xano/table/user.xs`; verificar com `xano_validate_xanoscript` — feito em 11/11/2026, sem erros
- [x] 1.2 Reescrever `auth/signup` com validação dos novos campos, unicidade de e-mail e CPF, perfil sempre `member` e códigos de erro (`email_taken`, `cpf_taken`, `invalid_*`); verificar com `xano_validate_xanoscript` — feito em 11/11/2026, sem erros
- [x] 1.3 Remover dados do usuário do `event_log` em `auth/signup`, `auth/login`, `auth/me`, `reset/update_password` e `reset/magic_link_login` (antes gravavam o registro com o hash da senha ou o token de redefinição); verificar com `xano_validate_xanoscript` e com o teste `TestLogsSemDadosDeAutenticacao` — feito em 12/11/2026
- [x] 1.4 Criar o grupo `Admin` (canonical `revaulte-admin`) e `GET /admin/users` com `enforce_role` e saída sem dados sensíveis; verificar com `xano_validate_xanoscript` — feito em 11/11/2026, sem erros
- [ ] 1.5 Fazer cópia de segurança do workspace e dos registros de `user` e `event_log`, prévia `--dry-run` e apresentar ao usuário as alterações previstas; verificar a autorização antes do envio
- [ ] 1.6 Enviar pelo Xano CLI somente os arquivos desta Change (sem `--sync`, `--delete` nem `--force` automático); verificar por requisições: cadastro válido, e-mail/CPF repetidos, login inválido, `auth/me` sem token (401), `GET /admin/users` sem token (401), com Cliente (403) e com Administrador (200, sem CPF)
- [ ] 1.7 Decidir com o usuário o que fazer com os registros antigos do `event_log` que contêm o hash da senha (gravados pelo Quick Start antes desta Change) e se `GET /logs/user/my_events` deve continuar publicado; executar somente após a decisão
- [ ] 1.8 Definir o primeiro Administrador pelo painel do Xano (campo `role` de uma conta real do grupo); verificar o acesso a `/admin`

## 2. Frontend Reflex

- [x] 2.1 Criar `revaulte/auth.py` com validação (CPF, senha, data), tradução de erros, destino seguro após login, `AuthState` (cookie `revaulte_sessao`, `auth/me` a cada página protegida) e `AdminState`; e `auth_api_url`/`admin_api_url` em `config.py`; verificar com `tests/test_contas.py` — 130 testes passam em 12/11/2026
- [ ] 2.2 Páginas `/entrar` e `/cadastro` com formulários na identidade da Revaulte, mensagens em `aria-live` e botão desabilitado durante o envio; verificar com testes de componente e no navegador
- [ ] 2.3 Páginas `/conta` e `/admin` (lista de usuários, “Acesso restrito” para Cliente) com `on_load` de proteção; verificar com testes e no navegador
- [ ] 2.4 Menu “Minha conta” dinâmico (Entrar / Cadastrar, Meu perfil, Painel administrativo, Sair) e `verificar_sessao` no `on_load` das páginas públicas; atualizar `tests/test_navegacao.py`; verificar no navegador em 1280 e 375 px
- [ ] 2.5 Estilos dos formulários e das páginas de conta em `styles.css`, com movimento reduzido; verificar sem rolagem horizontal a 375 px

## 3. Documentação e verificação

- [ ] 3.1 Atualizar `docs/domain-model.md` (Conta: `member` = Cliente, `admin` = Administrador; primeiro Administrador pelo painel) e `frontend/README.md` (variáveis `REVAULTE_AUTH_API_URL` e `REVAULTE_ADMIN_API_URL`)
- [ ] 3.2 Executar os testes, `reflex compile` e `openspec validate contas-acesso --strict`; percorrer no navegador todos os cenários da spec após o envio ao Xano
