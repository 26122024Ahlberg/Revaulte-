# Proposal

## Why

Cadastro e login são a base das funcionalidades restantes da Revaulte: favoritos, simulações salvas, anúncios publicados pelos próprios usuários, chat interno (cancelado em 26/11/2026) e área administrativa. Hoje o menu “Minha conta” mostra apenas itens “Em breve”, e o workspace Xano tem somente os endpoints de autenticação do modelo inicial (Quick Start), que ainda gravam o registro completo do usuário — incluindo o hash da senha — no `event_log` e incluem endpoints publicados sem autenticação.

## What Changes

- Cadastro de Cliente com nome, CPF, e-mail, telefone, data de nascimento, endereço e senha (`docs/project-overview.md`, seção 4), com e-mail e CPF únicos.
- Login com e-mail e senha, sessão mantida no navegador por até 24 horas (validade do token do Xano) e “Sair”.
- Perfis de acesso Cliente (`member`) e Administrador (`admin`); o cadastro público sempre cria Cliente.
- Página “Minha conta” (`/conta`) com os dados do próprio usuário, restrita a usuários autenticados.
- Painel administrativo básico (`/admin`) restrito a Administradores, contendo somente a lista de usuários (sem CPF, telefone, data de nascimento, endereço nem senha), servida por um endpoint que verifica o perfil no backend.
- Menu “Minha conta” passa a depender da sessão: “Entrar” e “Cadastrar” para visitantes; “Minha conta”, “Painel administrativo” (somente Administrador) e “Sair” para usuários autenticados; os demais itens continuam “Em breve”.
- Correção de segurança: os endpoints de cadastro, login, `auth/me` e redefinição de senha deixam de gravar dados do usuário no `event_log`.
- Plano de correção dos registros antigos do `event_log` que contêm o hash da senha ou o token de redefinição. Nenhum registro é apagado nesta etapa; a execução depende de cópia de segurança e autorização.
- Documentação da proteção dos endpoints do Quick Start publicados sem autenticação ou fora do escopo (`message/send_welcome_email`, `reset/request-reset-link`, `reset/magic-link-login` e `logs/user/my_events`). A aplicação dessa proteção no Xano depende de autorização.
- Compatibilidade com Windows: o fuso `America/Sao_Paulo` usado nas validações e datas deixa de exigir a base IANA do sistema operacional.

### Fora do escopo

- Recuperação de senha por e-mail, confirmação de e-mail, login social e autenticação em dois fatores.
- Edição do perfil e exclusão da conta (Change futura).
- Bloqueio de usuários, troca de perfil, moderação de anúncios e demais funções do painel (Change `administracao-moderacao`).
- Criação do primeiro Administrador pela interface: é feita pelo painel do Xano, alterando o campo `role` de uma conta existente.
- Exclusão ou alteração de registros do `event_log` e alterações no workspace Xano sem autorização explícita do usuário.

## Capabilities

### New Capabilities

- `contas-acesso`: cadastro, login, sessão, perfis Cliente/Administrador, painel administrativo básico e controle de acesso às páginas protegidas.

### Modified Capabilities

- `navegacao-site`: o requisito “Menu da conta” passa a variar conforme a sessão (Entrar, Cadastrar, Minha conta, Painel administrativo, Sair), e o requisito “Menu em tela estreita” deixa de fixar cinco itens na seção “Minha conta”. Delta MODIFIED em `specs/navegacao-site/spec.md`.

## Impact

- **Backend Xano** (somente após autorização): tabela `user` ganha `cpf`, `phone`, `birth_date` e `address` (sensíveis); `auth/signup` valida e grava os novos campos; `auth/login`, `auth/signup`, `auth/me`, `reset/update_password` e `reset/magic_link_login` deixam de registrar dados do usuário (hash da senha, token de redefinição) no log; novo grupo de API `Admin` com `GET /admin/users`; proteção planejada dos endpoints inseguros do Quick Start; plano para os registros antigos do `event_log`.
- **Frontend Reflex**: `AuthState`, páginas `/entrar`, `/cadastro`, `/conta` e `/admin`, menu da conta, estilos dos formulários na identidade atual e fuso compatível com Windows em `revaulte/auth.py`.
- **Domínio e documentação**: `docs/domain-model.md` (Conta: perfis `member`/`admin`, primeiro Administrador), `frontend/README.md` (variáveis de ambiente) e registro dos endpoints inseguros e do plano de logs.
- **Desenvolvimento em paralelo**: a Change avança na branch `feat/contas-acesso-entrega`, independente do PR #2 (`fix/ajustes-pesquisa-visual-windows`), que não altera `navegacao-site` nem `contas-acesso`.
