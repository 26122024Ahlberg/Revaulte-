# Design

## Context

Motivação e escopo: ver `proposal.md`. Requisitos: ver `specs/catalogo-publico/spec.md`.

Estado atual observado no repositório:

- **Frontend**: só existe `frontend-rascunho/`, com `index.projeto.html` e `styles.projeto.css`. É uma página inicial estática (topo, hero com slider, faixa de diferenciais, seção “Veículos em destaque” com quatro cartões fixos e rodapé). O HTML referencia `styles.css`, `scripts.js` e `./img/*`, que não existem. Não há página de catálogo. O rascunho define a identidade visual: tema escuro, variáveis de cor em `:root`, fontes League Gothic e Poppins, e o componente `.card` (imagem, título, linha “ano · km”, preço).
- **Backend**: `xano/` contém o workspace “Ghost's Workspace” sincronizado, somente com a estrutura inicial do Xano: tabelas `user` e `event_log`, grupos de API `Authentication` e `Event Logs`, funções `Quick Start/*`, um addon e exemplos de IA. Não existe tabela de veículos. A pasta `xano/` contém apenas arquivos `.xs` (19 arquivos), sem credenciais: as credenciais do Xano CLI ficam em `~/.xano/`, fora do repositório. Ela ainda não foi incluída em nenhum commit, mas não é ignorada pelo Git e deve ser versionada (ver decisão 10).
- **Convenções locais do XanoScript**: nomes de tabelas e campos em inglês; enum com `values = [...]`; arquivo do grupo de API em `xano/api/<grupo>/<grupo>.xs`; endpoints em `xano/api/<grupo>/<caminho>_<VERBO>.xs`; endpoint público é o que não declara `auth`.
- **Frontend em HTML/CSS/JS puro (referência)**: durante a implementação foi criada em `frontend/` uma versão da página de catálogo em HTML, CSS e JavaScript puro (`catalogo.html`, `css/styles.css`, `js/config.js`, `js/catalogo.js`, `img/placeholder.svg`), já integrada ao endpoint público e conferida no navegador quanto à marca Revaulte e à exibição de um veículo. Depois disso o professor determinou que o frontend seja obrigatoriamente desenvolvido em Reflex (Python). Essa versão deixa de ser o frontend definitivo e passa a ser referência de comportamento e de identidade visual (ver decisão 11).
- **Ambiente local**: o Python disponível na máquina é 3.9.6, e o Reflex 0.10.0 (versão atual no PyPI) exige Python 3.11 ou superior.
- **Restrições**: frontend obrigatoriamente em Reflex (Python), por determinação do professor da disciplina; backend em Xano/XanoScript; sincronização pelo Xano CLI; o rascunho deve permanecer intacto; autorização e regras de visibilidade aplicadas no backend Xano.

## Goals / Non-Goals

**Goals:**

- Garantir no backend que veículos em Rascunho nunca saiam do Xano pela listagem pública.
- Criar o menor esquema de dados que atenda ao catálogo, de forma que as próximas Changes possam estendê-lo sem retrabalho.
- Estabelecer a estrutura definitiva do frontend e o padrão de comunicação com o Xano, reutilizáveis pelas próximas páginas.
- Manter a identidade visual do rascunho e o uso em telas pequenas.

**Non-Goals:**

- Modelar a Configuração Original completa (cor, motorização, câmbio), as Modificações e a galeria de imagens.
- Definir upload ou armazenamento definitivo de imagens.
- Criar endpoints de escrita ou qualquer operação administrativa.
- Paginação, filtros, busca e ordenação escolhida pelo usuário.
- Hospedagem ou publicação do frontend.

## Decisions

### 1. Tabela `vehicle` apenas com os dados do catálogo

Criar uma única tabela `vehicle` com:

| Campo | Tipo | Observação |
| --- | --- | --- |
| `id` | int | chave primária |
| `created_at` | timestamp | padrão `now` |
| `brand` | text | marca |
| `model` | text | modelo |
| `version` | text, opcional | versão |
| `year` | int | ano |
| `condition` | enum `new`, `used` | condição |
| `mileage` | int | quilometragem em km |
| `price` | decimal | preço em reais |
| `is_modified` | bool, padrão `false` | veículo modificado/preparado |
| `status` | enum `draft`, `available`, `sold`, padrão `draft` | estado |
| `cover_image_url` | text, opcional | URL da imagem de capa do veículo |

Justificativa: o modelo de domínio não é um esquema físico e o banco deve evoluir junto das funcionalidades. Marca, modelo, versão e ano pertencem conceitualmente à Configuração Original, mas são indispensáveis ao cartão do catálogo; ficam em `vehicle` agora, e os demais atributos (cor, motorização, câmbio) entram na Change de detalhes. Nomes em inglês seguem as tabelas existentes; a tradução para “Novo/Usado”, “Vendido” e “Modificado” é responsabilidade da interface.

O padrão `draft` para `status` faz com que um registro criado sem estado explícito não seja publicado por engano.

Alternativas consideradas:

- *Criar já as tabelas de configuração original, modificações e imagens*: descartado; antecipa decisões que o modelo de domínio lista como indefinidas (seção 14).
- *Indicar “modificado” pela existência de registros de modificação*: descartado; depende de uma tabela que ainda não existe. O campo `is_modified` atende ao catálogo e pode ser mantido ou derivado depois.

### 2. Imagem de capa como URL opcional, com imagem provisória local como substituta

`cover_image_url` armazena a URL da imagem de capa do veículo, isto é, a imagem real daquele veículo exibida no cartão do catálogo. O campo é opcional.

A imagem provisória é um arquivo local do frontend (`frontend/assets/placeholder.svg`, servido como `/placeholder.svg`) e não é armazenada em `cover_image_url`. Ela é utilizada apenas em dois casos:

- quando a capa está ausente (campo vazio, nulo ou com endereço que não seja `http`/`https`);
- quando a capa falha ao carregar.

Em todos os outros casos o cartão exibe a imagem indicada por `cover_image_url`.

Justificativa: `docs/project-overview.md` deixa em aberto o uso do armazenamento do Xano para as imagens e permite imagens provisórias até que a gestão definitiva seja implementada. Guardar a capa como URL em um campo de texto não compromete essa decisão futura; o que é provisório nesta Change é a forma de armazenamento (URL em texto, sem upload), não o conteúdo do campo.

Alternativa considerada: campo do tipo `image` do Xano. Descartado nesta Change porque exige definir o fluxo de upload, que pertence à administração de veículos.

### 3. Endpoint público de leitura em grupo de API próprio

Criar o grupo de API `Catalog` e o endpoint `GET vehicles`, sem `auth`, sem parâmetros de entrada.

- O `canonical` do grupo deve ser único na instância Xano; o valor adotado é `ghostpay-catalog`. Ele leva o nome do grupo acadêmico (GhostPay) e foi criado antes da definição de que a loja se chama Revaulte; por ser um identificador técnico já em funcionamento, não é renomeado por causa da marca.
- O endereço público segue o formato `<base da instância>/api:<canonical>/vehicles`.
- A resposta é uma lista JSON; cada item contém somente `id`, `brand`, `model`, `version`, `year`, `condition`, `mileage`, `price`, `is_modified`, `status` e `cover_image_url`.

Justificativa: um grupo próprio separa o que é público do que exige autenticação e dá às próximas Changes (detalhes, filtros) um lugar natural. Os grupos existentes tratam de autenticação e logs e não devem receber endpoints de catálogo.

O endpoint não chama `Quick Start/log_event`: essa função registra ações de usuários autenticados, e o catálogo é anônimo.

### 4. Visibilidade por lista de estados permitidos, aplicada na consulta

A consulta filtra por `status` igual a `available` ou `sold`, em vez de `status` diferente de `draft`, e seleciona explicitamente os campos de saída.

Justificativa: com lista de permitidos, um estado criado no futuro não se torna público por omissão; com seleção explícita de campos, uma coluna acrescentada depois não vaza pelo endpoint público. As duas regras ficam no backend, como exige `AGENTS.md`; o frontend não filtra rascunhos, pois nunca os recebe.

Alternativa considerada: filtrar no JavaScript. Descartado; os dados de rascunho ficariam visíveis na resposta da rede.

### 5. Ordenação fixa e listagem completa

A listagem é devolvida por `created_at` decrescente (mais recentes primeiro), sem paginação.

Justificativa: é necessária uma ordem estável para que a página não mude a cada carregamento, e a ordem por data de criação não cria regra de negócio. Ordenações escolhidas pelo usuário pertencem à Change de filtros e ordenação. A visão geral descreve o catálogo como “listagem completa”, e o volume esperado em um projeto acadêmico é pequeno.

Alternativa considerada: veículos disponíveis antes dos vendidos. Descartado por ser uma regra de apresentação ainda não definida nos documentos.

### 6. Frontend definitivo em Reflex, na pasta `frontend/`

O frontend é um aplicativo Reflex com nome de app `revaulte`:

```
frontend/
├── rxconfig.py            rx.Config(app_name="revaulte")
├── requirements.txt       reflex com versão fixada
├── README.md              instalação e execução local
├── assets/
│   ├── styles.css         identidade visual (portada de frontend-html/css/styles.css)
│   └── placeholder.svg    imagem provisória (copiada de frontend-html/img/)
└── revaulte/
    ├── __init__.py
    ├── revaulte.py        rx.App, página /catalogo e redirecionamento de /
    ├── config.py          endereço base da API do catálogo
    ├── state.py           CatalogState: requisição ao Xano e preparação dos cartões
    └── components.py      topo, rodapé, cartão, selos e mensagens de estado
```

Pastas geradas pelo Reflex ou pelo ambiente Python (`.web/`, `.states/`, `.venv/`, `__pycache__/`) não são versionadas e entram no `.gitignore`.

- A página do catálogo fica na rota `/catalogo`. Por ser a única página desta Change, a rota `/` redireciona para `/catalogo`, para que `reflex run` abra diretamente o catálogo; a página inicial pertence a outra Change.
- O título da página é “Catálogo | Revaulte”. O topo exibe a marca Revaulte e o item “Catálogo” como página atual; o rodapé usa Revaulte; o nome GhostPay não aparece na interface. Itens para páginas inexistentes (Home, Financiamento, Contato) não são incluídos.
- Ambiente: Python 3.11 ou superior (proposto: Python 3.12 instalado pelo Homebrew), com ambiente virtual em `frontend/.venv` e dependências por `pip install -r requirements.txt`. A versão do Reflex é fixada em `requirements.txt` após a instalação. O uso de `uv`, recomendado pela documentação do Reflex, não é adotado para não introduzir outra ferramenta; pode ser revisto se o grupo preferir.
- Execução local: `reflex run` dentro de `frontend/`. Hospedagem continua fora do escopo.

Justificativa: o professor determinou o uso obrigatório de Reflex. Manter o nome `frontend/` preserva o local definitivo previsto na visão geral; separar estado, componentes e configuração deixa a comunicação com o Xano reutilizável pelas próximas páginas.

Alternativa considerada: criar o app Reflex em outra pasta e manter a versão HTML em `frontend/`. Descartado porque a pasta definitiva passaria a conter código que não é mais o frontend oficial.

### 7. Comunicação com o Xano feita pelo servidor do Reflex

O Reflex executa o estado e os manipuladores de eventos em Python, no servidor do próprio app, e envia ao navegador apenas os valores do estado. Por isso:

- A requisição `GET <base>/vehicles` é feita em um manipulador de eventos assíncrono de `CatalogState`, disparado pelo `on_load` da página e pelo botão “Tentar novamente”, usando um cliente HTTP assíncrono com tempo limite (proposto: `httpx`, já instalado como dependência do Reflex; confirmar na instalação).
- O navegador não acessa o Xano diretamente. A configuração de CORS do grupo `Catalog` deixa de ser relevante para o frontend.
- O endereço base fica em `revaulte/config.py`, lido da variável de ambiente `REVAULTE_CATALOG_API_URL` e, na ausência dela, de um valor padrão com o endereço público atual (`https://x8ki-letl-twmt.n7.xano.io/api:ghostpay-catalog`). O endereço não é credencial e pode ser versionado; nenhum token ou chave é necessário nem deve ser incluído.
- A regra de visibilidade continua no Xano: o servidor do Reflex recebe somente veículos Disponíveis e Vendidos e não refiltra nem amplia a lista.
- O estado guarda apenas os dados necessários aos cartões, derivados dos onze campos públicos, para que nada além deles chegue ao navegador.

Justificativa: é o modelo de execução do Reflex; fazer a requisição no navegador exigiria JavaScript próprio, contrariando o uso do framework.

### 8. Renderização segura e estados da página

- Os cartões são renderizados com `rx.foreach` sobre a lista do estado e com componentes de texto do Reflex, que exibem os dados como texto. Não se usa `rx.html` nem qualquer inserção de HTML a partir de dados do backend.
- O estado converte cada veículo da resposta em um item de exibição: título (marca, modelo e versão quando houver, sem espaços sobrando), linha de detalhes (ano · quilometragem · condição), preço formatado, indicadores de vendido e modificado e endereço da capa.
- Preço formatado no padrão brasileiro em Python (por exemplo, `R$ 118.900,00`), sem depender da configuração de localidade do sistema; quilometragem com separador de milhar e sufixo “km”; condição traduzida para “Novo” ou “Usado”.
- Capa: `cover_image_url` só é usado quando for um endereço `http` ou `https`; caso contrário o cartão já nasce com a imagem provisória `/placeholder.svg`. Quando a capa falha ao carregar no navegador, o evento de erro da imagem dispara um evento do estado que troca aquele cartão para a imagem provisória (ver decisão 2). Como `rx.el.img` e `rx.image` não aceitam `on_error` no Reflex 0.10.0 (confirmado na tarefa 6.3), a capa usa o componente `ImagemCapa` de `components.py`, uma extensão do elemento de imagem do Reflex que declara o gatilho `on_error`; não há biblioteca nova nem `rx.html`.
- Uma região da página alterna entre quatro estados (carregando, lista, vazio e erro) a partir de uma variável do estado, com `rx.cond`/`rx.match`. O estado de erro tem o botão “Tentar novamente”. Falha de rede, tempo esgotado, status HTTP de erro ou corpo que não seja uma lista são tratados como erro, e a lista é esvaziada para que nenhum veículo seja exibido.
- Selos “Modificado” e “Vendido” são textos sobre a imagem do cartão. O cartão vendido tem aparência esmaecida, sem destaque de preço e sem efeito de elevação; nenhum cartão é link ou possui ação de negociação.
- A grade mantém os pontos de quebra 4, 2 e 1 colunas.

### 9. Dados de teste inseridos manualmente no workspace

Como o cadastro administrativo está fora do escopo, os registros de verificação são criados diretamente no painel do Xano, cobrindo: disponível original usado, disponível modificado usado, disponível novo original, novo modificado, vendido original, vendido modificado, rascunho, um veículo sem versão e um sem imagem.

Alternativa considerada: endpoint ou tarefa de carga de dados. Descartado; criaria um caminho de escrita sem autorização definida.

### 10. Pasta `xano/` versionada no Git, sem credenciais

Os arquivos `.xs` de `xano/` são o código-fonte do backend e devem ser versionados. O estado inicial sincronizado (estrutura padrão do Xano) deve entrar em um commit próprio antes da criação dos arquivos desta Change, para que o `git diff` da implementação mostre somente o que ela acrescenta.

O `.gitignore` da raiz do repositório exclui arquivos de credenciais e de ambiente (`.env*`, `credentials.yaml`, `.xano/`, chaves), como proteção caso algum deles venha a ser criado dentro do projeto. Nenhuma regra ignora `xano/` ou arquivos `.xs`.

Justificativa: sem versionamento não há histórico nem revisão do backend, e `AGENTS.md` exige revisar o `git diff`. As credenciais do Xano CLI ficam em `~/.xano/credentials.yaml`, fora do repositório, e os arquivos sincronizados não contêm tokens nem chaves (o único campo de credencial presente, `bearer_token` em `xano/ai/tool/search_xano_docs.xs`, está vazio).

### 11. Identidade visual e versão HTML como referência

- A versão em HTML/CSS/JS puro é movida de `frontend/` para `frontend-html/` antes da criação do app Reflex, sem alterações de conteúdo, e passa a ser versionada como referência. Nada é apagado. `frontend-rascunho/` continua intacto.
- A identidade visual é preservada portando `frontend-html/css/styles.css` para `frontend/assets/styles.css`, carregado com `rx.App(stylesheets=["/styles.css", <Google Fonts>])`. Os componentes usam os elementos HTML do Reflex (`rx.el.*`) com as mesmas classes (`topbar`, `logo`, `cards`, `card`, `card-sold`, `badge`, `state-message`, `footer` etc.), mantendo cores, fontes League Gothic e Poppins, tema escuro e pontos de quebra.
- O tema padrão do Reflex (Radix) não deve sobrepor a identidade da Revaulte: configurar a aparência escura e conferir no navegador que fundo, fontes e cores correspondem à versão HTML.

Justificativa: reaproveitar a folha de estilos já conferida reduz o risco de divergência visual e mantém a página comparável lado a lado com a referência.

Alternativa considerada: reescrever todos os estilos como propriedades `style` dos componentes Reflex. Descartado nesta Change por duplicar trabalho sem ganho funcional; pode ser feito depois, se necessário.

## Risks / Trade-offs

- [O `canonical` escolhido pode já existir na instância Xano] → usar um valor específico do projeto e ajustá-lo se o envio pelo CLI acusar conflito; o endereço fica somente em `frontend/revaulte/config.py`.
- [`rx.el.img`/`rx.image` não aceitam o gatilho `on_error` no Reflex 0.10.0, necessário ao cenário “Imagem de capa indisponível”] → confirmado na tarefa 6.3. Mitigado com o componente `ImagemCapa`, que estende o elemento de imagem do Reflex declarando o gatilho; testado no Safari, o evento disparou uma vez para cada capa inválida e nenhuma vez para a capa válida. Solução aprovada pelo usuário. Uma atualização do Reflex pode alterar essa extensão: reexecutar o teste da capa quebrada ao atualizar a versão fixada.
- [O tema padrão do Reflex pode sobrepor fontes, cores ou espaçamentos de `styles.css`] → configurar a aparência escura e comparar a página Reflex com `frontend-html/` no navegador.
- [Python 3.9.6 na máquina, abaixo do mínimo do Reflex (3.11)] → instalar Python 3.12 e usar ambiente virtual próprio em `frontend/.venv`; a instalação depende de aprovação do usuário.
- [O Reflex baixa ferramentas de frontend (Node/Bun) na primeira execução e cria arquivos gerados] → ignorar `.web/` e `.states/` no Git e registrar no `README` do frontend os comandos de instalação e execução.
- [Requisição ao Xano feita pelo servidor do Reflex: a aba de rede do navegador não mostra mais a chamada ao Xano] → a verificação de que dados de Rascunho não chegam ao navegador passa a inspecionar as mensagens do WebSocket do Reflex, além da resposta do endpoint.
- [Listagem sem paginação cresce com o número de veículos] → aceitável para o volume esperado; paginação fica para a Change de filtros e ordenação, sem mudança de contrato além de novos parâmetros opcionais.
- [Marca, modelo, versão e ano em `vehicle` podem ser movidos quando a Configuração Original for modelada] → a resposta do endpoint é um contrato independente do esquema; a mudança ficaria restrita ao backend.
- [URLs de imagem de capa externas podem sair do ar] → a imagem provisória local cobre a falha; a gestão definitiva de imagens virá em Change própria.
- [Sintaxe de XanoScript presumida incorretamente] → consultar o Xano Developer MCP e validar cada arquivo `.xs` antes do envio.
- [Endpoint público sem limite de requisições] → é somente leitura e expõe apenas dados já públicos; limitação de taxa não é tratada nesta Change.

## Migration Plan

1. Criar os arquivos `.xs` localmente e validá-los com o Xano Developer MCP.
2. Enviar a tabela e, em seguida, o grupo de API e o endpoint ao workspace com o Xano CLI.
3. Inserir os registros de teste e conferir a resposta do endpoint.
4. ~~Criar o frontend em HTML/CSS/JS e apontar `config.js` para o endpoint~~ — feito; a versão passa a ser referência.
5. Preparar o ambiente Python 3.11+ e instalar o Reflex.
6. Mover a versão HTML para `frontend-html/` e criar o app Reflex em `frontend/`, portando a folha de estilos e a imagem provisória.
7. Implementar estado, componentes e página; verificar todos os cenários da spec na página Reflex.

O backend Xano já publicado não muda com a migração.

Reversão: a Change é apenas aditiva. Basta remover o grupo de API `Catalog`, a tabela `vehicle` e as pastas `frontend/` e `frontend-html/`; nenhuma estrutura existente é alterada.

## Open Questions

- Texto do selo: os documentos admitem “Modificado” ou “Preparado”. Adotado “Modificado”; a troca é apenas de rótulo.
- Gerenciador de ambiente Python: decidido pelo usuário — `venv` + `pip` com Python 3.12 do Homebrew e `reflex==0.10.0` fixado.
