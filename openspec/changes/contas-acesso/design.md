# Design

## Context

Requisitos: `specs/contas-acesso/spec.md`. O workspace já tem a tabela `user` (com `password` como tipo `password`, que o Xano grava como hash, e `role` enum `admin`/`member`) e os endpoints `auth/signup`, `auth/login` e `auth/me` do grupo `Authentication` (canonical `shCFXLjC`). O frontend Reflex conversa com o Xano pelo servidor do Reflex (o navegador não acessa o Xano diretamente), padrão mantido aqui.

## Goals / Non-Goals

**Goals:** fluxo completo de cadastro, login e saída; autorização aplicada no backend; nenhum dado pessoal exposto além do necessário; reaproveitar os endpoints do Quick Start.

**Non-Goals:** recuperação de senha, edição de perfil, gestão de usuários pelo Administrador.

## Decisions

### 1. Reaproveitar `user` e os endpoints do Quick Start

Não se cria tabela “cliente” separada: `user` representa a Conta e os dados cadastrais do Cliente. Perfis: `member` = Cliente, `admin` = Administrador (valores técnicos mantidos; rótulos em português só na interface). O cadastro público grava sempre `role = "member"` (já é assim no Quick Start); não há entrada de perfil no cadastro.

### 2. Campos de cadastro

`cpf` (texto com 11 dígitos), `phone` (texto com 10 ou 11 dígitos, DDD + número), `birth_date` (`date`) e `address` (texto livre, até 200 caracteres), todos `sensitive = true` e opcionais na tabela (contas antigas do Quick Start continuam válidas), mas obrigatórios no endpoint de cadastro. Unicidade do CPF verificada no endpoint por `db.get` (como o e-mail); não se cria índice único porque contas antigas têm CPF nulo. O backend confere formato (11 dígitos, não todos iguais) e unicidade; o frontend confere também os dígitos verificadores antes de enviar. Data de nascimento: no passado e posterior a 1900; nenhuma idade mínima é presumida.

### 3. Senha

Mantida a política da tabela (`min:8|minAlpha:1|minDigit:1`), repetida no frontend com mensagem em português. O hash é feito pelo tipo `password` do Xano; a senha nunca é registrada em log nem guardada no estado do Reflex depois do envio.

### 4. Sessão no navegador

O token devolvido pelo Xano (validade de 86 400 s) fica em um cookie `revaulte_sessao` declarado como `rx.Cookie` (`max_age` de 24 h, `same_site="strict"`, caminho `/`). A cada página protegida, o `on_load` chama `GET auth/me` com o token: o perfil exibido vem sempre do backend, nunca de um valor guardado no navegador. Token inválido ou expirado limpa o cookie e trata o usuário como visitante. Trade-off: o cookie é gravado pelo JavaScript do Reflex e não pode ser `HttpOnly`; aceitável no escopo acadêmico, registrado nos riscos.

### 5. Controle de acesso

- Backend: `auth/me` exige token (`auth = "user"`); `GET /admin/users` exige token e chama `Quick Start/enforce_role` com `required_role = "admin"` (403 para Cliente, 401 sem token).
- Frontend: `/conta` e `/admin` redirecionam para `/entrar?proximo=<rota>` sem sessão; Cliente em `/admin` vê “Acesso restrito”. A proteção do frontend é só de interface; a segurança está no backend.

### 6. Logs

`auth/signup`, `auth/login`, `auth/me`, `reset/update_password` e `reset/magic_link_login` passam a registrar apenas `{}` como `metadata` (antes gravavam o registro inteiro do usuário, inclusive o hash da senha e o token de redefinição). Um teste automatizado impede que `metadata: $user` volte a qualquer endpoint. Registros antigos do `event_log` não são apagados por esta Change; a limpeza (e a permanência do endpoint `GET /logs/user/my_events`, que devolve esses registros ao próprio usuário) é decidida pelo usuário (tarefa 1.7).

### 7. Mensagens de erro

O login responde sempre “E-mail ou senha incorretos.” (sem revelar se o e-mail existe). No cadastro, e-mail e CPF já cadastrados geram mensagens próprias, como no Quick Start. O frontend traduz os erros do Xano; nenhum texto técnico é exibido.

### 8. Configuração

Novas variáveis opcionais `REVAULTE_AUTH_API_URL` (padrão `.../api:shCFXLjC`) e `REVAULTE_ADMIN_API_URL` (padrão definido após a criação do grupo `Admin`, com canonical `revaulte-admin`). São endereços públicos, sem credenciais.

## Risks / Trade-offs

- [Cookie legível por JavaScript] → `same_site=strict`, validade de 24 h, nenhum dado pessoal no cookie (só o token); revisão quando houver domínio público com HTTPS.
- [Dados pessoais sensíveis (CPF, endereço)] → `sensitive = true` no Xano, nunca devolvidos em listagens nem no log; `auth/me` devolve apenas ao próprio usuário.
- [Primeiro Administrador] → definido manualmente no painel do Xano pelo grupo.
- [Envio ao Xano] → cópia de segurança, prévia `--dry-run` e envio parcial sem `--sync`/`--delete`, somente com autorização do usuário.
