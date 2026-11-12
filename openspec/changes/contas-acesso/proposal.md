# Proposal

## Why

Cadastro e login são a base das funcionalidades restantes da Revaulte: favoritos, simulações salvas, anúncios publicados pelos próprios usuários, chat interno e área administrativa. Hoje o menu “Minha conta” mostra apenas itens “Em breve”, e o workspace Xano tem somente os endpoints de autenticação do modelo inicial (Quick Start), que ainda gravam o registro completo do usuário — incluindo o hash da senha — no `event_log`.

## What Changes

- Cadastro de Cliente com nome, CPF, e-mail, telefone, data de nascimento, endereço e senha (`docs/project-overview.md`, seção 4), com e-mail e CPF únicos.
- Login com e-mail e senha, sessão mantida no navegador por até 24 horas (validade do token do Xano) e “Sair”.
- Perfis de acesso Cliente (`member`) e Administrador (`admin`); o cadastro público sempre cria Cliente.
- Página “Minha conta” (`/conta`) com os dados do próprio usuário, restrita a usuários autenticados.
- Área administrativa inicial (`/admin`) restrita a Administradores, com a lista de usuários (sem CPF, telefone, endereço nem senha), servida por um endpoint que verifica o perfil no backend.
- Menu “Minha conta” passa a mostrar “Entrar / Cadastrar” ou “Minha conta”, “Painel administrativo” (somente Administrador) e “Sair”; os demais itens continuam “Em breve”.
- Correção de segurança: os endpoints de cadastro, login, `auth/me` e redefinição de senha deixam de gravar dados do usuário no `event_log`.

### Fora do escopo

- Recuperação de senha por e-mail, confirmação de e-mail, login social e autenticação em dois fatores.
- Edição do perfil e exclusão da conta (Change futura).
- Bloqueio de usuários, troca de perfil e moderação de anúncios (Change `administracao-moderacao`).
- Criação do primeiro Administrador pela interface: é feita pelo painel do Xano, alterando o campo `role` de uma conta existente.

## Capabilities

### New Capabilities

- `contas-acesso`: cadastro, login, sessão, perfis Cliente/Administrador e controle de acesso às páginas protegidas.

### Modified Capabilities

- `navegacao-site` (Change `navegacao-principal`, ainda não arquivada): itens “Entrar / Cadastrar” e “Meu perfil” deixam de ser “Em breve”. O delta MODIFIED será acrescentado no arquivamento de `navegacao-principal`.

## Impact

- **Backend Xano** (somente após autorização): tabela `user` ganha `cpf`, `phone`, `birth_date` e `address` (sensíveis); `auth/signup` valida e grava os novos campos; `auth/login`, `auth/signup`, `auth/me`, `reset/update_password` e `reset/magic_link_login` deixam de registrar dados do usuário (hash da senha, token de redefinição) no log; novo grupo de API `Admin` com `GET /admin/users`.
- **Frontend Reflex**: `AuthState`, páginas `/entrar`, `/cadastro`, `/conta` e `/admin`, menu da conta e estilos dos formulários na identidade atual.
- **Domínio e documentação**: `docs/domain-model.md` (Conta: perfis `member`/`admin`, primeiro Administrador) e `frontend/README.md` (variáveis de ambiente).
