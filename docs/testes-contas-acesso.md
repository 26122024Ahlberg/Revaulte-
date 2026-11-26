# Revaulte — Roteiro de testes das contas de acesso

Roteiro manual de ponta a ponta para a Change `contas-acesso`: cadastro, login, Minha conta, Sair, área administrativa e menu. Complementa os testes automáticos (`frontend/tests/`), que simulam o Xano e não acessam a rede.

## Antes de começar

> **26/11/2026:** a Change foi arquivada com ressalvas (`openspec/changes/archive/2026-11-26-contas-acesso/tasks.md`). Este roteiro não foi executado por inteiro. Nas linhas 4.1 e 4.6, o destino “/” vale para páginas públicas; em teste simulado, “Sair” em página protegida terminou na tela de login.

- **Autorização**: as etapas 2 em diante criam contas no Xano (workspace `v1`, live). Só execute com autorização da equipe e apague as contas ao final (etapa 9).
- **Dados fictícios**: use e-mails do domínio reservado `example.com` e CPFs gerados por um gerador de CPF de teste. Nunca use dados de pessoas reais. Não anote senhas, CPFs ou tokens em arquivos do repositório.
- **Limite do Xano**: 10 requisições a cada 20 s. Faça uma ação por vez e espere alguns segundos entre elas. Uma mensagem “Não foi possível concluir agora…” logo após muitas ações seguidas indica o limite, não um defeito.
- **Ambiente**: `reflex run` em `frontend/` e o site em `http://localhost:3000/`. Use uma janela anônima/InPrivate para começar sem sessão.
- **Larguras**: repita as etapas marcadas com 📱 em 375 px (ferramentas do desenvolvedor → modo dispositivo).

Contas sugeridas:

| Conta | Nome | E-mail | Uso |
| --- | --- | --- | --- |
| C | Cliente Teste Revaulte | `cliente.teste@example.com` | Cliente |
| A | Admin Teste Revaulte | `admin.teste@example.com` | Administrador (cargo trocado no painel) |

## 1. Visitante (sem criar conta)

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 1.1 | Abrir `/` e acionar ☰ 📱 | “Minha conta” mostra **Entrar**, **Cadastrar**, Anunciar veículo, Meus anúncios e Favoritos como links; nada de “Minha conta”, “Painel administrativo” ou “Sair” |
| 1.2 | Acionar “Favoritos” | Vai para `/entrar?proximo=/favoritos` |
| 1.3 | Abrir `/conta` | Vai para `/entrar?proximo=/conta` |
| 1.4 | Abrir `/admin` | Vai para `/entrar?proximo=/admin` |
| 1.5 | Em `/entrar`, enviar vazio | “Informe e-mail e senha.”; nenhuma requisição ao Xano |
| 1.6 | Em `/entrar`, e-mail inexistente com qualquer senha | “E-mail ou senha incorretos.” |
| 1.7 | Em `/entrar`, acionar “Cadastre-se” | Abre `/cadastro` |

## 2. Cadastro com dados inválidos (nada é enviado ao Xano)

Em `/cadastro` 📱, preencha tudo corretamente e altere um campo por vez:

| # | Campo alterado | Mensagem esperada |
| --- | --- | --- |
| 2.1 | Nome vazio | “Informe seu nome completo.” |
| 2.2 | E-mail `teste@` | “Informe um e-mail válido.” |
| 2.3 | CPF `111.111.111-11` | “Informe um CPF válido.” |
| 2.4 | Telefone `1234` | “Informe o telefone com DDD.” |
| 2.5 | Data de nascimento no futuro | “Informe uma data de nascimento válida.” |
| 2.6 | Endereço `Rua` | “Informe seu endereço.” |
| 2.7 | Senha `abc123` | “A senha deve ter pelo menos 8 caracteres.” |
| 2.8 | Senha `abcdefgh` ou `12345678` | “A senha deve ter pelo menos uma letra (A–Z) e um número (0–9).” |
| 2.9 | Confirmação diferente | “As senhas não coincidem.” |

Durante cada envio válido, o botão mostra “Criando conta…” e fica desabilitado.

## 3. Cadastro e Minha conta (Cliente C) — cria conta

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 3.1 | Cadastrar a conta C com dados válidos | Vai para `/conta`; mostra nome, e-mail e perfil **Cliente**; não mostra CPF, telefone, nascimento, endereço nem senha |
| 3.2 | Acionar ☰ 📱 | **Minha conta**, Anunciar veículo, Meus anúncios, Favoritos e **Sair**; sem “Painel administrativo”, “Entrar” ou “Cadastrar” |
| 3.3 | Tentar cadastrar outra conta com o mesmo e-mail (maiúsculas e espaços) | “Este e-mail já está cadastrado. Entre com ele ou use outro.” |
| 3.4 | Tentar cadastrar com o mesmo CPF e outro e-mail | “Este CPF já está cadastrado.” |
| 3.5 | No painel do Xano, abrir a conta C | `role = member`; `birth_date` igual à data informada, sem deslocamento de dia |

## 4. Sair e entrar (Cliente C)

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 4.1 | ☰ → **Sair** | Volta para `/`; o menu volta a mostrar Entrar e Cadastrar |
| 4.2 | Abrir `/conta` | Vai para `/entrar?proximo=/conta` |
| 4.3 | Entrar com a senha errada | “E-mail ou senha incorretos.” |
| 4.4 | Entrar com a senha certa | Botão “Entrando…” e, em seguida, `/conta` |
| 4.5 | Abrir `/admin` | “Acesso restrito”; a lista de usuários não é carregada |
| 4.6 | Em `/conta`, acionar **Sair** | Volta para `/`, sem sessão |

## 5. Administrador (conta A) — cria conta e altera cargo no painel

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 5.1 | Cadastrar a conta A pelo site e sair | Perfil Cliente em `/conta` |
| 5.2 | No painel do Xano, trocar o `role` da conta A para `admin` | — |
| 5.3 | Entrar com a conta A a partir de `/admin` (`/entrar?proximo=/admin`) | Volta para `/admin` |
| 5.4 | Ver a lista 📱 | Colunas ID, Data de cadastro, Nome, E-mail e Perfil; as duas contas, a mais recente primeiro; sem rolagem horizontal em 375 px (cada usuário vira um bloco) |
| 5.5 | Acionar ☰ | **Minha conta**, **Painel administrativo**, Anunciar veículo, Meus anúncios, Favoritos e **Sair** |
| 5.6 | Abrir `/conta` | Perfil **Administrador** |

## 6. Conta sem cargo (teste C3)

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 6.1 | No painel do Xano, deixar o `role` da conta C vazio | — |
| 6.2 | Entrar com a conta C e abrir `/admin` | “Acesso restrito”; o site trata a conta sem cargo como Cliente e nem chama `GET admin/users` |
| 6.2b | Somente com autorização: chamar `GET admin/users` direto (ferramenta de API) com o token da conta C | 403 `forbidden`, sem dados (comprova a proteção no backend) |
| 6.3 | Restaurar o `role` da conta C para `member` | — |

## 7. Sessão inválida

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 7.1 | Autenticado com a conta C, excluir a conta C no painel do Xano | — |
| 7.2 | Recarregar `/conta` | A sessão é removida e o site vai para `/entrar?proximo=/conta` |

## 8. Navegadores

Repita 1.1, 1.3, 4.1 e 5.3 no Edge, no Chrome e no Opera. No Opera, conferir se `/entrar?proximo=/conta` mantém o parâmetro (pendência da tarefa 3.7).

## 9. Limpeza (obrigatória)

1. No painel do Xano, excluir as contas A e C.
2. Conferir `user = 0` (ou só as contas reais da equipe) e anotar quantos registros de teste ficaram no `event_log`. O `event_log` só é limpo com autorização da equipe.
3. Fechar a janela anônima.

## Registro de resultados

Para cada etapa, anote data, navegador, largura e “ok” ou a diferença encontrada. Não registre senhas, CPFs, tokens nem e-mails reais.
