# Design

## Context

Motivação e escopo: ver `proposal.md`. Requisitos: ver `specs/catalogo-publico/spec.md`.

Estado atual observado no repositório:

- **Frontend**: só existe `frontend-rascunho/`, com `index.projeto.html` e `styles.projeto.css`. É uma página inicial estática (topo, hero com slider, faixa de diferenciais, seção “Veículos em destaque” com quatro cartões fixos e rodapé). O HTML referencia `styles.css`, `scripts.js` e `./img/*`, que não existem. Não há página de catálogo. O rascunho define a identidade visual: tema escuro, variáveis de cor em `:root`, fontes League Gothic e Poppins, e o componente `.card` (imagem, título, linha “ano · km”, preço).
- **Backend**: `xano/` contém o workspace “Ghost's Workspace” sincronizado, somente com a estrutura inicial do Xano: tabelas `user` e `event_log`, grupos de API `Authentication` e `Event Logs`, funções `Quick Start/*`, um addon e exemplos de IA. Não existe tabela de veículos. A pasta `xano/` contém apenas arquivos `.xs` (19 arquivos), sem credenciais: as credenciais do Xano CLI ficam em `~/.xano/`, fora do repositório. Ela ainda não foi incluída em nenhum commit, mas não é ignorada pelo Git e deve ser versionada (ver decisão 10).
- **Convenções locais do XanoScript**: nomes de tabelas e campos em inglês; enum com `values = [...]`; arquivo do grupo de API em `xano/api/<grupo>/<grupo>.xs`; endpoints em `xano/api/<grupo>/<caminho>_<VERBO>.xs`; endpoint público é o que não declara `auth`.
- **Restrições**: HTML, CSS e JavaScript puro, sem framework; backend em Xano/XanoScript; sincronização pelo Xano CLI; o rascunho deve permanecer intacto; autorização e regras de visibilidade aplicadas no backend.

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

A imagem provisória é um arquivo local do frontend (`frontend/img/placeholder.svg`) e não é armazenada em `cover_image_url`. Ela é utilizada apenas em dois casos:

- quando a capa está ausente (campo vazio, nulo ou com endereço que não seja `http`/`https`);
- quando a capa falha ao carregar.

Em todos os outros casos o cartão exibe a imagem indicada por `cover_image_url`.

Justificativa: `docs/project-overview.md` deixa em aberto o uso do armazenamento do Xano para as imagens e permite imagens provisórias até que a gestão definitiva seja implementada. Guardar a capa como URL em um campo de texto não compromete essa decisão futura; o que é provisório nesta Change é a forma de armazenamento (URL em texto, sem upload), não o conteúdo do campo.

Alternativa considerada: campo do tipo `image` do Xano. Descartado nesta Change porque exige definir o fluxo de upload, que pertence à administração de veículos.

### 3. Endpoint público de leitura em grupo de API próprio

Criar o grupo de API `Catalog` e o endpoint `GET vehicles`, sem `auth`, sem parâmetros de entrada.

- O `canonical` do grupo deve ser único na instância Xano; usar um valor específico do projeto, como `ghostpay-catalog`.
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

### 6. Estrutura definitiva do frontend em `frontend/`

```
frontend/
├── catalogo.html
├── css/
│   └── styles.css
├── js/
│   ├── config.js      endereço base da API
│   └── catalogo.js    carregamento e renderização
└── img/
    └── placeholder.svg
```

Justificativa: a visão geral determina que a estrutura definitiva seja criada separadamente do rascunho. `styles.css` é escrito do zero, reaproveitando do rascunho as variáveis de cor, a tipografia, os botões, o topo, o rodapé e o componente `.card`; os estilos do hero, do slider e da faixa de diferenciais não são levados, pois não pertencem ao catálogo. Nada em `frontend-rascunho/` é editado, movido ou importado por caminho.

O topo da página de catálogo exibe a marca e o item “Catálogo” como página atual. Itens para páginas ainda inexistentes (Home, Financiamento, Contato) não são incluídos, para não criar links quebrados.

### 7. Comunicação com o Xano por `fetch`, com endereço em arquivo de configuração

`config.js` expõe o endereço base do grupo de API; `catalogo.js` faz uma requisição `GET` com `fetch` ao carregar a página.

Justificativa: `fetch` é nativo e dispensa bibliotecas. O endereço do endpoint público não é credencial e pode ser versionado; mantê-lo em um único arquivo evita repeti-lo nas próximas páginas. Nenhum token ou chave é necessário nem deve ser incluído.

### 8. Renderização segura e estados da página

- Os cartões são montados com `createElement` e `textContent`, nunca com `innerHTML` a partir de dados do backend, pois os textos virão futuramente de cadastro administrativo.
- `cover_image_url` é usado como `src` da capa quando for um endereço `http` ou `https`. A imagem provisória local só entra quando a capa está ausente (ou o endereço não é `http`/`https`) ou quando o evento de erro da imagem indica falha no carregamento (ver decisão 2).
- Preço formatado com `Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })`; quilometragem com separador de milhar e sufixo “km”.
- Uma região da página alterna entre quatro estados: carregando, lista, vazio e erro. O estado de erro tem um botão “Tentar novamente” que repete a requisição. Resposta com status HTTP de erro ou corpo que não seja uma lista é tratada como erro.
- Selos: “Modificado” e “Vendido” são elementos de texto sobre a imagem do cartão. O cartão vendido recebe uma classe que reduz o destaque visual (imagem esmaecida e preço sem a cor de destaque) e não tem efeito de elevação ao passar o cursor. Como esta Change não possui página de detalhes nem contato, nenhum cartão é link ou possui ação de negociação.
- A grade de cartões mantém os pontos de quebra do rascunho (4, 2 e 1 colunas).

### 9. Dados de teste inseridos manualmente no workspace

Como o cadastro administrativo está fora do escopo, os registros de verificação são criados diretamente no painel do Xano, cobrindo: disponível original usado, disponível modificado usado, disponível novo original, novo modificado, vendido original, vendido modificado, rascunho, um veículo sem versão e um sem imagem.

Alternativa considerada: endpoint ou tarefa de carga de dados. Descartado; criaria um caminho de escrita sem autorização definida.

### 10. Pasta `xano/` versionada no Git, sem credenciais

Os arquivos `.xs` de `xano/` são o código-fonte do backend e devem ser versionados. O estado inicial sincronizado (estrutura padrão do Xano) deve entrar em um commit próprio antes da criação dos arquivos desta Change, para que o `git diff` da implementação mostre somente o que ela acrescenta.

O `.gitignore` da raiz do repositório exclui arquivos de credenciais e de ambiente (`.env*`, `credentials.yaml`, `.xano/`, chaves), como proteção caso algum deles venha a ser criado dentro do projeto. Nenhuma regra ignora `xano/` ou arquivos `.xs`.

Justificativa: sem versionamento não há histórico nem revisão do backend, e `AGENTS.md` exige revisar o `git diff`. As credenciais do Xano CLI ficam em `~/.xano/credentials.yaml`, fora do repositório, e os arquivos sincronizados não contêm tokens nem chaves (o único campo de credencial presente, `bearer_token` em `xano/ai/tool/search_xano_docs.xs`, está vazio).

## Risks / Trade-offs

- [O `canonical` escolhido pode já existir na instância Xano] → usar um valor específico do projeto e ajustá-lo se o envio pelo CLI acusar conflito; o endereço fica somente em `config.js`.
- [CORS pode bloquear a requisição quando a página é aberta por `file://` ou por um servidor local] → verificar a configuração de CORS do grupo de API no Xano e testar a página servida por um servidor HTTP local simples.
- [Listagem sem paginação cresce com o número de veículos] → aceitável para o volume esperado; paginação fica para a Change de filtros e ordenação, sem mudança de contrato além de novos parâmetros opcionais.
- [Marca, modelo, versão e ano em `vehicle` podem ser movidos quando a Configuração Original for modelada] → a resposta do endpoint é um contrato independente do esquema; a mudança ficaria restrita ao backend.
- [URLs de imagem de capa externas podem sair do ar] → a imagem provisória local cobre a falha; a gestão definitiva de imagens virá em Change própria.
- [Sintaxe de XanoScript presumida incorretamente] → consultar o Xano Developer MCP e validar cada arquivo `.xs` antes do envio.
- [Endpoint público sem limite de requisições] → é somente leitura e expõe apenas dados já públicos; limitação de taxa não é tratada nesta Change.

## Migration Plan

1. Criar os arquivos `.xs` localmente e validá-los com o Xano Developer MCP.
2. Enviar a tabela e, em seguida, o grupo de API e o endpoint ao workspace com o Xano CLI.
3. Inserir os registros de teste e conferir a resposta do endpoint.
4. Criar o frontend e apontar `config.js` para o endpoint.

Reversão: a Change é apenas aditiva. Basta remover o grupo de API `Catalog`, a tabela `vehicle` e a pasta `frontend/`; nenhuma estrutura existente é alterada.

## Open Questions

- Texto do selo: os documentos admitem “Modificado” ou “Preparado”. Adotado “Modificado”; a troca é apenas de rótulo.
