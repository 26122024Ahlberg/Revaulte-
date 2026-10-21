# Design

## Context

Requisitos: ver `specs/detalhes-veiculo/spec.md`. O Xano tem a tabela `vehicle` com os onze campos de catálogo e o endpoint público `GET /vehicles` (somente `available`/`sold`, campos explícitos). Não há dados técnicos nem modificações. Alterações no Xano dependem de autorização do usuário após revisão desta proposta; por isso a entrega é em duas etapas.

## Goals / Non-Goals

**Goals:** página funcional já com o backend atual; troca de fonte de dados localizada em uma única função; backend aditivo, sem alterar `GET /vehicles`.

**Non-Goals:** galeria, regularização, administração.

## Decisions

### 1. Duas etapas com a mesma interface

- **Etapa A (sem mudar o Xano)**: `DetalheState.carregar` busca `GET /vehicles` e seleciona o item pelo `id`. A visibilidade continua garantida pelo backend: Rascunho nunca está na lista. Dados técnicos e modificações ficam vazios; a seção de modificações de um veículo modificado mostra “detalhes não informados”.
- **Etapa B (após autorização)**: a mesma função passa a chamar `GET /vehicles/{vehicle_id}`; 404 vira “não encontrado”, outras falhas viram erro.

A busca fica em uma função `buscar_veiculo(id)` em `state.py`, que devolve o veículo, “não encontrado” ou erro; a página não muda entre as etapas.

### 2. Rota dinâmica e identificador

Rota `/veiculo/[id]` do Reflex. O identificador é validado no estado (inteiro positivo) antes de qualquer requisição; inválido resulta em “não encontrado”. Confirmar no Reflex 0.10 o acesso ao parâmetro da rota (`self.router.page.params` ou variável de rota) com um teste mínimo no início da implementação.

### 3. Item de exibição do detalhe

Um `DetalheVeiculo` (dataclass) reutiliza as funções de formatação do catálogo (`formatar_titulo`, `formatar_preco`, `formatar_quilometragem`, `endereco_capa`) e acrescenta `cor`, `motorizacao`, `cambio`, `descricao` e `modificacoes: list[Modificacao(area, descricao)]`, com as áreas traduzidas para português. Somente esses campos chegam ao navegador.

### 4. Cartões como links

`cartao_veiculo` passa a envolver o cartão em `rx.el.a(href="/veiculo/<id>")` (exige `id` no cartão, previsto em `navegacao-principal`). O cartão vendido continua clicável, pois a página informa a indisponibilidade. Estilo de foco visível em `styles.css`.

### 5. Interesse demonstrativo

Botão “Tenho interesse” que alterna uma variável do estado e exibe uma mensagem fixa: “O contato com o anunciante ainda não está disponível nesta versão do site.” Nenhuma requisição, nenhum dado de contato.

### 6. Backend (etapa B, depende de autorização)

- `vehicle`: campos opcionais `text color?`, `text engine?`, `text transmission?`, `text description?` (com `filters=trim`). Aditivo; registros existentes não mudam.
- Tabela `vehicle_modification`: `id`, `created_at`, `vehicle_id` (referência a `vehicle`), `area` (enum `engine`, `forced_induction`, `power`, `fuel`, `transmission`, `suspension`, `wheels_tires`, `brakes`, `interior`, `exterior`, `other`, seguindo as áreas do domínio) e `description` (text). Sem campo de regularização.
- Endpoint `GET vehicles/{vehicle_id}` no grupo `Catalog`, sem `auth`: consulta única com `id` igual ao informado **e** `status` em `available`/`sold` (mesma lista de permitidos), campos de saída explícitos, modificações do veículo com `area` e `description`; ausência resulta em erro 404 sem distinguir Rascunho de inexistente.
- Sintaxe de parâmetro de rota, consulta única, relação e erro 404 a confirmar no Xano Developer MCP e validar com `xano_validate_xanoscript` antes do envio pelo Xano CLI.

Alternativa: guardar as modificações em um campo de texto livre em `vehicle`. Descartada: o domínio define Modificação como entidade com área, e a lista estruturada é o diferencial da Revaulte.

## Risks / Trade-offs

- [Autorização do Xano atrasar] → etapa A já atende página, preço, condição, selos, interesse e não encontrado.
- [Parâmetro de rota no Reflex 0.10 diferente do esperado] → teste mínimo na tarefa 1.1, antes da página.
- [Sintaxe XanoScript presumida] → MCP e validação antes do envio.
- [Endpoint revela existência de Rascunho] → mesma resposta 404 para Rascunho e inexistente; verificado por teste.

## Migration Plan

Etapa B: validar os `.xs`, enviar a tabela alterada, a nova tabela e o endpoint pelo Xano CLI, inserir dados de teste e só então trocar a função de busca. Reversão: voltar a função para a etapa A; as alterações no Xano são aditivas e podem ser removidas sem afetar `GET /vehicles`.
