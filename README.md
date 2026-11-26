# Revaulte

Marketplace web de veículos clássicos, antigos, esportivos, raros e modificados/preparados. A Revaulte apresenta os veículos anunciados, mostra a configuração original e as modificações de cada um, oferece uma simulação informativa de financiamento e permite criar conta, entrar e acessar uma área administrativa.

Projeto acadêmico desenvolvido pelo grupo **GhostPay**. O nome do produto é **Revaulte**; GhostPay aparece apenas em identificadores técnicos antigos, como o repositório e o workspace do Xano.

Repositório: https://github.com/26122024Ahlberg/Revaulte-

## Tecnologias

| Parte | Tecnologia |
| --- | --- |
| Frontend | [Reflex](https://reflex.dev) 0.10 (Python 3.12), exigido pela disciplina |
| Backend | [Xano](https://www.xano.com) com XanoScript (workspace “Ghost's Workspace”, branch `v1`) |
| Especificação | [OpenSpec](https://github.com/Fission-AI/OpenSpec) (Explore → Propose → Review → Apply → Verify → Archive) |

## Estrutura

| Pasta | Conteúdo |
| --- | --- |
| `frontend/` | Aplicativo Reflex (páginas, estado, estilos e testes). Ver `frontend/README.md` |
| `xano/` | Código XanoScript do backend (tabelas, endpoints e funções), sincronizado pelo Xano CLI |
| `openspec/` | Especificações (`specs/`), Changes em andamento (`changes/`), concluídas (`changes/archive/`) e canceladas (`changes-canceladas/`) |
| `docs/` | Visão geral, modelo de domínio, guia de colaboração e roteiros de teste e de vídeo |
| `frontend-html/`, `frontend-rascunho/` | Versões anteriores em HTML/CSS/JS, mantidas só como referência |

## Como executar

Requisitos: Python 3.12 e acesso à internet na primeira execução (o Reflex baixa o Bun e os pacotes JavaScript para `frontend/.web/`).

**Windows (PowerShell)**, dentro de `frontend/`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
reflex run
```

**macOS/Linux**, dentro de `frontend/`:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
reflex run
```

O site abre em `http://localhost:3000/`. Detalhes do Windows (política de execução do PowerShell, UTF-8) estão em `docs/colaboracao.md`.

O frontend usa o backend já publicado no Xano; não é preciso configurar nada para executar. Os endereços podem ser trocados por variáveis de ambiente (ver `frontend/README.md`).

## Manual de uso

### Visitante (sem conta)

- **Home (`/`)**: carrossel de destaques, veículos em destaque e a proposta da Revaulte.
- **Estoque (`/estoque`), Usados (`/usados`) e Modificados (`/modificados`)**: catálogo com pesquisa por texto e filtros de condição e modificação.
- **Página do veículo (`/veiculo/<id>`)**: fotos, ficha técnica, configuração original, modificações e preparação, anunciante, contato por WhatsApp (quando informado) e simulador de financiamento (somente para veículo disponível; valores ilustrativos, sem valor de proposta).
- **Menu ☰ → Minha conta**: “Entrar”, “Cadastrar”, “Anunciar veículo”, “Meus anúncios” e “Favoritos”; os três últimos levam ao login quando não há sessão.

### Criar conta (`/cadastro`)

Todos os campos são obrigatórios: nome completo, e-mail, CPF (com dígitos verificadores válidos), telefone com DDD, data de nascimento, endereço, senha e confirmação. A senha precisa ter **no mínimo 8 caracteres, com pelo menos uma letra (A–Z) e um número (0–9)**. E-mail ou CPF já cadastrados são recusados com mensagem própria. Após o cadastro, o usuário já fica autenticado e vai para “Minha conta”.

### Entrar e sair

- **Entrar (`/entrar`)**: e-mail e senha. Credenciais erradas mostram sempre “E-mail ou senha incorretos.”, sem revelar se o e-mail existe.
- A sessão dura até 24 horas.
- **Sair** (menu ☰ ou página Minha conta): apaga a sessão do navegador e volta à página inicial.

### Cliente

- **Minha conta (`/conta`)**: nome, e-mail e perfil (Cliente). CPF, telefone, data de nascimento, endereço e senha não são exibidos.
- Abrir `/conta` sem estar autenticado leva ao login e, depois dele, de volta à conta.

- **Anunciar veículo (`/anunciar`)**: formulário de anúncio (sem fotos). O anúncio nasce como Rascunho, fica fora do catálogo e é publicado pela equipe no painel do Xano. O nome de exibição do anunciante é pedido só no primeiro anúncio (limite de 20 rascunhos por conta).
- **Meus anúncios (`/meus-anuncios`) e ficha (`/meus-anuncios/<id>`)**: somente os anúncios da própria conta, com o estado de cada um. Não há edição nem exclusão nesta versão.
- **Favoritos**: botão “Favoritar” / “Remover dos favoritos” na página do veículo e lista em `/favoritos`. Veículos vendidos continuam na lista; os que deixam de ser públicos não aparecem. Depende do grupo `Favoritos` do Xano, já publicado.

### Administrador

- **Painel administrativo (`/admin`, também no menu ☰)**: lista de usuários com ID, data de cadastro, nome, e-mail e perfil, do mais recente para o mais antigo. Não há ações de edição, bloqueio ou troca de perfil nesta versão.
- Cliente que abre `/admin` vê “Acesso restrito”. A permissão é conferida no backend: o endpoint `GET admin/users` responde 401 sem token e 403 para quem não é Administrador.
- **Primeiro Administrador**: não há tela para isso. A equipe cria uma conta pelo site e, no painel do Xano, altera o campo `role` dessa conta de `member` para `admin`.

## Testes e validações

Dentro de `frontend/`, com o ambiente ativado:

```powershell
$env:PYTHONUTF8 = "1"          # Windows; no macOS/Linux não é necessário
python -m unittest discover -s tests -v
reflex compile
```

Na raiz do repositório:

```bash
openspec validate contas-acesso --strict
openspec validate --all
```

Em 26/11/2026, `openspec validate --all --strict` passa em todos os itens, sem avisos.

Os testes automáticos não acessam a rede (o Xano é simulado). O roteiro de testes manuais de ponta a ponta, com dados fictícios, está em `docs/testes-contas-acesso.md`.

## Segurança

- Nenhum token, senha ou credencial é versionado; o token de sessão fica só no cookie `revaulte_sessao` do navegador.
- As senhas são armazenadas pelo Xano somente como hash; os registros de evento não guardam senha, hash, CPF, telefone, data de nascimento nem endereço.
- O perfil de acesso é sempre conferido no backend; esconder itens do menu é apenas interface.
- Os endpoints de exemplo do Quick Start do Xano considerados inseguros (envio de e-mail de boas-vindas, link de redefinição de senha e login por link mágico) foram desativados e respondem 404. O `GET logs/user/my_events` foi restringido a `id`, `created_at` e `action` da própria conta; essa correção e a regra da data de nascimento no cadastro (data de hoje em Brasília) foram publicadas no Xano em 24/11/2026 e verificadas em execução (a data de hoje é recusada; `my_events` só devolve `id`, `created_at` e `action` da própria conta). Detalhes em `docs/seguranca-endpoints-quick-start.md`.

## Limitações conhecidas

- O plano do Xano aceita 10 requisições a cada 20 segundos; acima disso o site mostra “Muitas tentativas em pouco tempo…” em login, cadastro, anúncios e favoritos.
- Recuperação de senha e confirmação de e-mail não existem nesta versão. Anúncios pelo site não têm fotos, edição nem exclusão.
- Não há chat interno: o contato entre comprador e vendedor é feito exclusivamente pelo WhatsApp, quando o anunciante autoriza (a Change `chat-interno` foi cancelada em 26/11/2026).
- Favoritos: a tabela `favorite` e o grupo `Favoritos` estão publicados no Xano e foram testados manualmente no navegador (favoritar, listar por conta e remover). Não foram testados em execução o índice único nem envios simultâneos. Em 26/11/2026 a tabela tinha 3 registros, que devem ser preservados.
- Em um teste no Opera, o endereço `/entrar` apareceu sem o parâmetro `?proximo=`; não foi reproduzido em outros navegadores (tarefa 3.7 da Change `contas-acesso`).

## Documentação

- `docs/project-overview.md`: visão geral, problema, objetivos e público.
- `docs/domain-model.md`: conceitos do domínio.
- `docs/colaboracao.md`: preparação do Windows e fluxo com branches.
- `docs/testes-contas-acesso.md`: roteiro de testes manuais das contas.
- `docs/testes-anuncios-cliente.md`: roteiro de testes de anúncios dos Clientes.
- `docs/testes-favoritos.md`: roteiro de testes de Favoritos.
- `docs/seguranca-endpoints-quick-start.md`: endpoints do Quick Start desativados e logs de eventos.
- `docs/roteiro-fechamento-openspec.md`: roteiro de fechamento das Changes e pendências.
- `docs/roteiro-video.md`: roteiro do vídeo de apresentação.
- `openspec/changes/contas-acesso/`: proposta, decisões (`design.md`), requisitos e tarefas das contas de acesso.
