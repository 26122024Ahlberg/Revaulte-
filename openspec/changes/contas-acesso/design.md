# Design

## Context

Requisitos: `specs/contas-acesso/spec.md`. O workspace já tem a tabela `user` (com `password` como tipo `password`, que o Xano grava como hash, e `role` enum `admin`/`member`) e os endpoints `auth/signup`, `auth/login` e `auth/me` do grupo `Authentication` (canonical `shCFXLjC`). O frontend Reflex conversa com o Xano pelo servidor do Reflex (o navegador não acessa o Xano diretamente), padrão mantido aqui.

## Goals / Non-Goals

**Goals:** fluxo completo de cadastro, login e saída; autorização aplicada no backend; nenhum dado pessoal exposto além do necessário; reaproveitar os endpoints do Quick Start.

**Non-Goals:** recuperação de senha, edição de perfil, gestão de usuários pelo Administrador (bloqueio, troca de perfil), exclusão de registros do `event_log` nesta etapa.

## Decisões do usuário (18/11/2026)

- **D1** — Painel administrativo básico: somente a lista de usuários (decisão 5).
- **D2** — Corrigir a compatibilidade de fuso no Windows (decisão 9).
- **D3** — Planejar a correção dos logs sensíveis, sem apagar registros nesta etapa (decisão 6).
- **D4** — Documentar a proteção dos endpoints inseguros (decisão 10).
- **D5** — Continuar em paralelo ao PR #2 (decisão 12).

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

- Backend: `auth/me` exige token (`auth = "user"`); `GET /admin/users` exige token e chama `Quick Start/enforce_role` com `required_role = "admin"` antes de consultar a tabela.
- Respostas de permissão (corrigidas na etapa 4, 18/11/2026, somente nos arquivos locais):

  | Situação | `auth/me` | `GET /admin/users` | Antes |
  | --- | --- | --- | --- |
  | Sem token ou token inválido/expirado | 401 (`auth = "user"`) | 401 (`auth = "user"`) | igual |
  | Conta excluída com token ainda válido | 401 `unauthorized` | 401 `unauthorized` (`enforce_role`) | `auth/me`: 200 com corpo `null`; admin: 400 `inputerror` |
  | Conta sem cargo (`role` nulo) | 200; o frontend a trata como Cliente, sem privilégios | 403 `forbidden` | comportamento indefinido de `|get` com chave nula |
  | Cliente (`member`) | 200 | 403 `forbidden` | 403 por `throw`, com o cargo real na mensagem |
  | Administrador (`admin`) | 200 | 200 | igual |

  `enforce_role` usa só `precondition` (`unauthorized` → 401, `accessdenied` → 403), confere o cargo antes de usá-lo e não revela o cargo atual nas mensagens. O login responde 401 (`unauthorized`) com a mesma mensagem para e-mail inexistente, conta excluída e senha errada (antes, 403). O frontend já trata 401 e 403 de `auth/me` como sessão inválida, e 400/401/403/404 do login como “E-mail ou senha incorretos.”.
- Listagem administrativa: `output` fechado em `id`, `created_at`, `name`, `email` e `role`. Um teste falha se `password`, `password_reset`, `cpf`, `phone`, `birth_date` ou `address` aparecerem no endpoint; o frontend também descarta campos fora desses cinco.
- Frontend: `/conta` e `/admin` redirecionam para `/entrar?proximo=<rota>` sem sessão; Cliente em `/admin` vê “Acesso restrito”. A proteção do frontend é só de interface; a segurança está no backend.
- Painel administrativo básico (D1): `/admin` mostra apenas a tabela de usuários (identificador, nome, e-mail, perfil e data de cadastro), com estados “carregando”, “lista vazia” e “erro ao carregar”. Não há ações sobre os usuários nesta Change.

### 6. Logs

`auth/signup`, `auth/login`, `auth/me`, `reset/update_password` e `reset/magic_link_login` passam a registrar apenas `{}` como `metadata` (antes gravavam o registro inteiro do usuário, inclusive o hash da senha e o token de redefinição). Um teste automatizado impede que `metadata: $user` volte a qualquer endpoint.

Registros antigos (D3): nesta etapa **nenhum registro é apagado ou alterado**. O plano, executado somente após cópia de segurança e autorização do usuário, é:

1. Inventariar, sem alterar nada, quantos registros do `event_log` têm `metadata` com `password`, `password_reset` ou dados pessoais.
2. Apresentar ao usuário as opções: (a) substituir esses `metadata` por `{}` mantendo `user_id`, `action` e data (recomendada, preserva a trilha de auditoria); (b) apagar os registros; (c) manter, restringindo o acesso.
3. Até a decisão, restringir `GET /logs/user/my_events`, que devolve esses registros ao próprio usuário (ver decisão 10).
4. Verificar depois da execução que nenhum registro contém hash ou token.

### 9. Fuso horário compatível com Windows

`revaulte/auth.py` usa `ZoneInfo("America/Sao_Paulo")` para a data de hoje (validação da data de nascimento) e para formatar a data de cadastro. No Windows, o Python não tem a base IANA e, sem o pacote `tzdata`, a chamada levanta `ZoneInfoNotFoundError` já no `import` do módulo (confirmado em 18/11/2026). Decisão (D2, implementada na etapa 3): `FUSO = timezone(timedelta(hours=-3), "BRT")` em todos os sistemas, sem `ZoneInfo` — o Brasil não tem horário de verão desde 2019, então o resultado é o mesmo, e o comportamento fica idêntico no Windows, Linux e macOS. Não se acrescenta dependência. Alternativas descartadas: incluir `tzdata` em `requirements.txt` (dependência extra só para um fuso fixo) e `ZoneInfo` com contingência (dois caminhos de código para o mesmo resultado). Testes cobrem o deslocamento, a virada do dia em Brasília e a importação do módulo com `zoneinfo`/`tzdata` bloqueados.

### 10. Endpoints inseguros do Quick Start

O grupo `Authentication` herdou endpoints do modelo inicial que não fazem parte desta Change. Situação documentada (D4); a proteção no Xano só é aplicada com autorização, junto ao envio da tarefa 1.6:

| Endpoint | Problema | Proteção planejada |
| --- | --- | --- |
| `POST message/send_welcome_email` | Sem autenticação; aceita qualquer `user_id`, dispara e-mail e grava evento em nome de outro usuário | Exigir `auth = "user"` e usar `$auth.id` em vez de `user_id`, ou retirar da API pública (a Revaulte não usa e-mail de boas-vindas) |
| `GET reset/request-reset-link` | Recuperação de senha está fora do escopo; recebe o e-mail na URL, gera link para a página de demonstração do Quick Start e não limita tentativas | Retirar da API pública até a Change de recuperação de senha |
| `POST reset/magic-link-login` | Mesmo fluxo fora do escopo; emite token de sessão | Retirar da API pública junto com o anterior |
| `GET logs/user/my_events` | Exige token, mas devolve ao usuário registros antigos com hash da senha | Restringir a Administrador ou retirar até a correção dos logs (decisão 6) |

O documento de referência fica em `docs/` (tarefa 4.2). Nenhum desses endpoints é usado pelo frontend.

**Decisão (19/11/2026, opção A, somente arquivos locais):** `message/send_welcome_email`, `reset/request-reset-link` e `reset/magic-link-login` são **desativados no código**, sem exclusão: cada arquivo mantém nome, verbo, grupo `Authentication`, `tags` e `guid` publicados, com `input` vazio e uma pilha que contém apenas `precondition (false)` com `error_type = "notfound"` (resposta 404). O bloqueio não consulta nem altera o banco, não envia e-mail, não cria token ou sessão e não registra evento. A função `Quick Start/generate_magic_link` permanece, mas deixa de ser chamada (funções não são acessíveis externamente). Motivos para não excluir: o envio parcial do Xano CLI não remove objetos; a exclusão pelo CLI exigiria `--sync --delete` (marcado como **[CRITICAL]**), que também enviaria diferenças fora do escopo (`seller`, `vehicle`, catálogo); e a exclusão manual pelo painel deixaria o repositório diferente do workspace. Reversão: reenviar as versões do backup de 19/11/2026 (mesmo `guid`) com `-i`, após `--dry-run`. `logs/user/my_events` fica para depois: exige token, devolve só os registros do próprio usuário e o `event_log` está vazio (0 registros em 19/11/2026). Verificação: `TestEndpointsQuickStartDesativados` e, após o envio autorizado, requisições que devem responder 404 sem gravar no `event_log`.

### 11. Navegação (`navegacao-site`)

O delta MODIFIED troca o requisito “Menu da conta” (cinco itens “Em breve”) por um menu que depende da sessão confirmada no backend: visitante vê “Entrar” (link para `/entrar`) e “Cadastrar” (link para `/cadastro`); usuário autenticado vê “Minha conta” (link para `/conta`) e “Sair”; Administrador vê também “Painel administrativo” (link para `/admin`). “Anunciar veículo”, “Meus anúncios” e “Favoritos” continuam “Em breve”. O requisito “Menu em tela estreita” deixa de fixar a contagem de itens. Ocultar “Painel administrativo” é só interface; a autorização continua no backend.

Atualização (21/11/2026, tarefa 3.4): por decisão do usuário, o visitante vê “Entrar” e “Cadastrar” como itens separados (antes um só, “Entrar / Cadastrar”) e o item do usuário autenticado chama-se “Minha conta” (antes “Meu perfil”); o delta `navegacao-site` e o cenário “Sair” foram ajustados. As páginas públicas (`/`, `/estoque`, `/usados`, `/modificados`, `/veiculo/<n>` e a página 404) chamam `AuthState.verificar_sessao` ao abrir, que só consulta `auth/me` quando há token e a sessão ainda não foi conferida na conexão atual (uma chamada por conexão, não uma por página); `/conta` e `/admin` já consultam pelo `exigir_*`, e `/entrar` e `/cadastro` não consultam. Enquanto a primeira conferência não termina, o menu mostra os itens de visitante.
### 12. Desenvolvimento em paralelo ao PR #2

O trabalho segue na worktree `Revaulte-contas-acesso` (branch `feat/contas-acesso-entrega`, a partir da `main`). O PR #2 altera apenas `pesquisa-catalogo`, `visual-paginas-internas` e testes de animação; não há sobreposição com esta Change. Se o PR #2 for integrado antes, a branch é atualizada a partir da `main` antes do merge desta Change.

### 13. Destino seguro após o login

Etapa 3 (18/11/2026): `destino_seguro` deixou de aceitar qualquer caminho iniciado por `/` e passou a aceitar apenas uma lista fechada, comparada exatamente: `/`, `/estoque`, `/usados`, `/modificados`, `/conta`, `/admin` e `/veiculo/<n>` (inteiro positivo, sem zero à esquerda, até 12 dígitos, como `ler_id_veiculo`). Qualquer outro valor leva a `/conta`: URLs externas (`https://`, `//host`, `javascript:`, barra invertida), caminhos codificados (`%2F`), `..`, espaços, caracteres de controle, `?`, `#`, `/entrar`, `/cadastro` e rotas desconhecidas. Um teste compara a lista com as constantes de rota de `components.py` para detectar divergência.

### 14. Validação do XanoScript

Em 18/11/2026 a sessão de trabalho não tinha o Xano Developer MCP nem o Xano CLI disponíveis, portanto as alterações da etapa 4 (`enforce_role`, `auth/me`, `auth/login`, `admin/users`) usam apenas construções já presentes e validadas no repositório (`precondition` com `error_type`, `db.get`, `|get`) e são verificadas por testes estáticos (`TestPermissoesXano`). A validação com `xano_validate_xanoscript` fica pendente (tarefa 2.9) e é obrigatória antes da prévia `--dry-run`. Em 19/11/2026 a revisão da etapa 4 confirmou o mesmo cenário (MCP e CLI ainda indisponíveis); a verificação foi feita por `tests/test_contas.py` (35 testes), pela suíte completa (153 testes) e por `openspec validate contas-acesso --strict`. Nada foi enviado ao Xano.

Atualização (19/11/2026): com o Xano Developer MCP disponível, `xano_validate_xanoscript` aprovou, sem erros nem avisos, todos os arquivos do envio (tarefa 2.9 concluída), inclusive os três bloqueios da decisão 10 e as correções A6 e V9 (decisão 15). O Xano CLI 1.3.4 foi instalado e usado para cópia de segurança, prévias `--dry-run` e o envio autorizado.

### 15. Publicação e testes reais no Xano (19–20/11/2026)

**Publicação.** Workspace 169675, branch `v1` (live, única branch). Cópia de segurança em `xano-backups/2026-11-19/`, na pasta do usuário (fora do repositório; código e registros — `user` e `event_log` estavam vazios). Prévias `--dry-run` rodadas com uma trava externa que só deixa sair a requisição para `/multidoc/dry-run`, pois no CLI 1.3.4 uma prévia sem `summary` seguiria para o envio. Envio parcial com 11 filtros `-i` (9 atualizações, 2 criações, 0 exclusões), sem `--sync`, `--delete` nem `--force`, feito pelo usuário com confirmação manual; `--guids` gravou os GUIDs de `admin.xs` e `users_GET.xs` e `admin.xs` recebeu `swagger = {active: false}`, padrão aplicado pelo servidor. Depois de cada envio, nova prévia: “No changes to push”. Branch de teste descartada: só existe `v1`, a separação de dados entre branches não ficou confirmada na documentação e o envio era aditivo.

**Correções encontradas pelos testes e publicadas.**
- **A6** — `auth/login` sem e-mail respondia 400 “Missing param: field_value” (detalhe interno). Um `precondition` antes da consulta responde 401 “Invalid Credentials.” para e-mail ou senha ausentes ou vazios.
- **V9** — `auth/signup` aceitava `1990-02-30`: o `to_timestamp` converte dias inexistentes em outra data. Um `precondition` exige que `$nascimento|format_timestamp:"Y-m-d":"UTC"` seja igual ao texto recebido; conversão e formatação no mesmo fuso evitam deslocamento de dia. Verificado: `1990-02-30` e `2026-02-29` recusadas, `2000-02-29` aceita.

**Testes reais (dados fictícios, domínio `example.com`).** Fase A (sem gravação): `auth/me` e `admin/users` sem token ou com token inválido → 401; login com e-mail inexistente ou sem campos → 401. Fase A2: V1–V10 → 400 com o `invalid_*` esperado; cada caso levava um segundo campo inválido verificado depois do testado (endereço; no V10, e-mail e CPF já cadastrados), para que nenhuma falha de validação gravasse conta. Fase B: cadastro válido (200, só `authToken` e `user_id`), e-mail repetido e com maiúsculas/espaços (403 `email_taken`), CPF repetido (403 `cpf_taken`), login correto (200) e com senha errada (401), `auth/me` (200, cinco campos, `member`), `admin/users` como Cliente (403 `forbidden`). Fase C: com o cargo `admin` definido no painel, `admin/users` → 200, duas contas, cinco campos cada, mais recente primeiro. Fase D: tokens emitidos antes da exclusão das contas no painel → `auth/me` e `admin/users` 401 `unauthorized`, inclusive para o Administrador. Senhas, CPFs e tokens ficaram em arquivos temporários fora do repositório, com acesso restrito, excluídos ao final; o usuário excluiu as contas e os eventos de teste e confirmou `user = 0` e `event_log = 0`.

**Conferência no painel (B11).** O usuário confirmou `birth_date` gravado como `1990-05-10` (conta C) e `1985-01-31` (conta A), sem deslocamento de dia, e as duas contas criadas pelo cadastro com `role = member` (a conta A só passou a `admin` na fase C, pelo painel).

**Não verificado.** Conta sem cargo (403; teste C3 não executado).

**Limite de requisições.** O plano do Xano permite 10 requisições a cada 20 s e responde 429 `ERROR_CODE_TOO_MANY_REQUESTS` (ocorreu durante a fase A2). Os testes passaram a usar 6 s entre chamadas e a parar diante de 429. Para o site, o `auth/me` a cada página protegida e o catálogo consomem o mesmo limite; o tratamento do 429 no frontend fica para decisão (tarefa 3.6).

**Pendências registradas.**
- **B10 (senha forte) — corrigido e publicado em 20/11/2026 (tarefa 2.12).** O endpoint só exigia 8 caracteres; letra e número dependiam do filtro da tabela no `db.add`, sem `precondition` anterior que impedisse a gravação, por isso o teste não foi executado na fase B. O `precondition` de senha passou a exigir também `"/[A-Za-z]/"` e `"/[0-9]/"`, antes de qualquer consulta, gravação, token ou log. Verificado com endereço inválido como proteção: senha só com letras e só com números → 400 `invalid_password`; nova prévia: “No changes to push”.
- **Letras e dígitos fora do ASCII na senha (pendente, tarefa 2.14)** — o backend aceita só `A–Z`, `a–z` e `0–9`; o frontend usa `isalpha`/`isdigit`, que aceitam letras acentuadas e dígitos Unicode. Uma senha como `çççççç12` passa no frontend e recebe `invalid_password` (mensagem já traduzida). A forma Unicode (`\p{L}`) não foi usada no backend porque não está confirmada na documentação do Xano e poderia gerar erro em todo cadastro; a alternativa é o frontend adotar a regra ASCII.
- **Data de hoje** — o frontend recusa nascimento igual a hoje (`data >= hoje`); o backend aceita, porque compara a meia-noite UTC com `now`. Efeito pequeno; a regra a manter fica para decisão (tarefa 2.13).
- **Primeiro Administrador real** (tarefa 1.8) e **páginas Reflex** `/entrar`, `/cadastro`, `/conta`, `/admin` e menu (tarefas 3.2–3.5) continuam pendentes.

### 7. Mensagens de erro

O login responde sempre “E-mail ou senha incorretos.” (sem revelar se o e-mail existe), com HTTP 401 para e-mail inexistente, conta excluída, senha errada e e-mail ou senha ausentes ou vazios (correção A6, decisão 15). No cadastro, e-mail e CPF já cadastrados geram mensagens próprias, como no Quick Start. O frontend traduz os erros do Xano; nenhum texto técnico é exibido.

### 8. Configuração

Novas variáveis opcionais `REVAULTE_AUTH_API_URL` (padrão `.../api:shCFXLjC`) e `REVAULTE_ADMIN_API_URL` (padrão `.../api:revaulte-admin`; o grupo `Admin` foi criado no Xano em 19/11/2026 com esse canonical, confirmado depois do envio). São endereços públicos, sem credenciais.

## Risks / Trade-offs

- [Cookie legível por JavaScript] → `same_site=strict`, validade de 24 h, nenhum dado pessoal no cookie (só o token); revisão quando houver domínio público com HTTPS.
- [Dados pessoais sensíveis (CPF, endereço)] → `sensitive = true` no Xano, nunca devolvidos em listagens nem no log; `auth/me` devolve apenas ao próprio usuário.
- [Primeiro Administrador] → definido manualmente no painel do Xano pelo grupo.
- [Envio ao Xano] → cópia de segurança, prévia `--dry-run` e envio parcial sem `--sync`/`--delete`, somente com autorização do usuário (feito em 19/11/2026; decisão 15).
- [Registros antigos com hash permanecem até a decisão] → em 19/11/2026 o `event_log` estava vazio (sem registros antigos); `my_events` ainda sem a restrição prevista (tarefa 2.3).
- [Endpoints inseguros ativos até o envio autorizado] → `send_welcome_email`, `request-reset-link` e `magic-link-login` desativados e publicados em 19/11/2026 (404 verificado); `my_events` pendente.
- [Limite de 10 requisições a cada 20 s no plano do Xano] → respostas 429 possíveis com poucos acessos simultâneos; testes com intervalo de 6 s; tratamento no frontend pendente (tarefa 3.6).
- [Senha forte só no filtro da tabela] → resolvido em 20/11/2026: o endpoint exige 8 caracteres, letra e número antes da gravação (tarefa 2.12, B10). Resta a diferença ASCII × Unicode entre backend e frontend (tarefa 2.14).
- [Nascimento igual a hoje] → aceito pelo backend e recusado pelo frontend; alinhamento pendente (tarefa 2.13).
- [Deslocamento fixo −03:00] → correto enquanto o Brasil não adotar horário de verão; se isso mudar, rever a decisão 9 (por exemplo, `ZoneInfo` com `tzdata`).
- [Mudança em `Quick Start/enforce_role`, função compartilhada] → hoje só `GET /admin/users` a chama; os novos códigos (401 para conta excluída, 403 para conta sem cargo) valem para qualquer chamador futuro.
- [XanoScript não validado pelo MCP na etapa 4] → resolvido em 19/11/2026: todos os arquivos do envio validados com `xano_validate_xanoscript` antes da prévia (tarefa 2.9).
