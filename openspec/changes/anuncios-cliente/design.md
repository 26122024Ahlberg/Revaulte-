# Design

## Context

Estado observado em 23/11/2026, por auditoria somente de leitura de `origin/main` (`dda54f7`) e do código publicado no Xano (workspace 169675, branch `v1`, baixado com `xano workspace pull` para uma pasta temporária):

- **Catálogo**:
  - `GET /vehicles` devolve os seis veículos (ids 1 a 6), todos `available`;
  - o detalhe do Opala (id 1) devolve o anunciante “Vinicius Melo de Barros” com WhatsApp autorizado;
  - os demais veículos não têm anunciante.
- **Tabela `seller`** (Change `contato-vendedor`): `display_name`, `whatsapp`, `contact_authorized` e `contact_authorized_at`. Não há ligação com `user`. O `vehicle` aponta para o anunciante por `seller_id`.
- **Diferenças entre o código publicado e a pasta `xano/`**:
  - no publicado, `seller.contact_authorized` e `vehicle.is_modified` **não têm** o padrão `false` que os arquivos locais declaram;
  - o detalhe público está em `api/catalog/vehicles/vehicle_id_GET.xs` no publicado e em `api/catalog/vehicles_vehicle_id_GET.xs` no local;
  - as demais diferenças são só de formatação.
- **Contas** (Change `contas-acesso`):
  - `auth = "user"` responde 401 sem token;
  - `Quick Start/enforce_role` responde 401 para conta excluída e 403 para conta sem cargo ou com cargo insuficiente, sem revelar o cargo;
  - o frontend tem `AuthState._exigir`, `destino_seguro` (lista fechada), `chamar_xano` executado no servidor do Reflex e `AdminState` como modelo de página protegida.
- **Limite do plano do Xano**: 10 requisições a cada 20 s (429 `ERROR_CODE_TOO_MANY_REQUESTS`).
- As Changes `contas-acesso`, `contato-vendedor`, `catalogo-publico` e `detalhes-veiculo` ainda não foram arquivadas. O delta de `navegacao-site` desta Change parte da versão do menu definida por `contas-acesso`.

## Goals / Non-Goals

**Goals:**

- Ligar conta → anunciante → veículo de forma que o dono seja sempre derivado do token.
- Criar anúncios somente em Rascunho e permitir ao dono consultá-los, sem tocar nos endpoints públicos.
- Reaproveitar `enforce_role`, `AuthState`, `chamar_xano` e os padrões visuais das páginas de conta.

**Non-Goals:**

- Edição, exclusão ou troca de estado pelo Cliente.
- Envio de imagens, modificações por área, contato de anunciantes do site, moderação pelo `/admin`.
- Qualquer alteração em `vehicle`, `vehicle_modification`, `user`, nos endpoints do catálogo ou de autenticação, ou em registros existentes.

## Decisions

### 1. Vínculo pelo registro `seller_account` (arquitetura aprovada em 23/11/2026; tabela de registro escolhida pelo usuário na opção A, em 23/11/2026)

Nova tabela `seller_account` com `user_id` (referência a `user`) e `seller_id` (referência a `seller`), ambos obrigatórios e cada um com índice `btree|unique`. O veículo continua ligado ao anunciante por `vehicle.seller_id`. Um anúncio pertence à conta X quando `vehicle.seller_id = seller_account.seller_id` e `seller_account.user_id = X`.

- **Tabela `seller` sem alteração**: o anunciante do Opala e qualquer anunciante cadastrado pela equipe não têm registro em `seller_account`, então nunca aparecem em “Meus anúncios”. Veículos sem anunciante (`seller_id = 0`) também não casam com nenhum registro.
- **No máximo um anunciante por conta**: garantido pelo índice único em `user_id` (decisão 9), não por uma consulta prévia.
- **Por que uma tabela própria e não `seller.user_id` único**: a documentação do Xano não confirma se um índice único aceita vários nulos, e os anunciantes da equipe teriam `user_id` nulo (verificação da tarefa 2.1: a documentação do MCP 2.7.1 lista `btree|unique` sem tratar nulos; respostas da comunidade divergem). Em `seller_account` só entram linhas com conta real, então a unicidade não depende do tratamento de valores vazios.
- **Índice único em `seller_id`**: impede que um mesmo anunciante seja ligado a duas contas.
- **Alternativa descartada**: `vehicle.owner_user_id`. É mais simples, mas separa o dono do anúncio do anunciante exibido no site e contraria o modelo de domínio (“um Anunciante estará associado a uma Conta”).
- **Versão anterior** (`seller.user_id` opcional com índice `btree` simples) substituída nesta decisão; nunca foi publicada.

### 2. Estado inicial Rascunho, publicação pela equipe (aprovado em 23/11/2026)

O `POST` grava `status: "draft"` explicitamente. A equipe publica pelo painel do Xano, como já faz hoje. Como os endpoints públicos usam lista permitida (`available` ou `sold`), nenhum endpoint público precisa mudar para esconder os rascunhos.

### 3. Nome de exibição (decisão do usuário em 23/11/2026)

- **Primeiro anúncio**: o formulário mostra o campo “Nome de exibição”, preenchido com o nome da conta e editável (2 a 60 caracteres). O backend usa esse valor somente quando cria o anunciante.
- **Anúncios seguintes**: o formulário mostra o nome atual sem edição, e o backend ignora `display_name`. Assim um nome já publicado não muda sem passar pela equipe.
- **Nome da conta com mais de 60 caracteres**: o campo vem vazio e o Cliente o preenche.

### 4. Contato não autorizado

O anunciante criado pelo site recebe `contact_authorized: false` e `whatsapp` nulo, gravados explicitamente, porque o padrão `false` não existe no Xano publicado. O detalhe público já trata esse caso (nome sem número). A coleta de contato com consentimento fica para uma Change futura.

### 5. Endpoints: novo grupo `Anuncios`

Grupo com canonical `revaulte-anuncios` e `swagger = {active: false}`, como `Admin`. Todos os endpoints têm `auth = "user"` e começam com `function.run "Quick Start/enforce_role"` com `required_role: "member"`: Cliente e Administrador passam, conta sem cargo recebe 403 e conta excluída recebe 401.

| Endpoint | Entrada | Resposta |
| --- | --- | --- |
| `POST /anuncios` | `display_name?`, `brand`, `model`, `version?`, `year`, `condition`, `mileage`, `price`, `is_modified`, `color?`, `engine?`, `transmission?`, `description?` | `{id, status}` |
| `GET /anuncios` | nenhuma | `{anunciante: {display_name} \| null, anuncios: [...]}` |
| `GET /anuncios/{vehicle_id}` | `vehicle_id` | ficha do anúncio ou 404 |

- **Lista**: em ordem decrescente de criação, cada item com `id`, `brand`, `model`, `version`, `year`, `condition`, `mileage`, `price`, `is_modified`, `status` e `created_at`.
- **Ficha**: os mesmos campos da lista mais `color`, `engine`, `transmission` e `description`.
- **Saídas** sempre com `output` fechado. Nunca saem `seller_id`, `user_id`, `whatsapp`, `contact_*` nem dados de `user`. As consultas internas ao registro `seller_account` leem `seller_id` só para decidir o anunciante, e esse valor nunca entra em `response`.
- **Campos aceitos**: só os declarados em `input` são lidos. `status`, `seller_id`, `user_id`, `cover_image_url`, `id` e `created_at` não existem na entrada e são gravados pelo próprio endpoint (`draft`, anunciante da conta, nulo, automático). A tarefa 2.4 verifica se o Xano ignora campos não declarados.
- **Ficha de anúncio alheio**: a consulta filtra por `vehicle.id` **e** pelo registro `seller_account` da conta. Sem anunciante, ou sem registro, a resposta é 404 `notfound`, idêntica para anúncio alheio, da equipe ou inexistente.
- **`GET /anuncios`** existe para que `/anunciar` saiba se a conta já tem anunciante (decisão 3) e para que `/meus-anuncios` use uma única requisição.
- Nenhum endpoint grava no `event_log`, evitando dados de anúncio em logs.

### 6. Limites de validação (backend e frontend iguais)

| Campo | Regra | Erro |
| --- | --- | --- |
| `brand` | obrigatório, 1–40 caracteres | `invalid_brand` |
| `model` | obrigatório, 1–60 | `invalid_model` |
| `version` | opcional, até 80 | `invalid_version` |
| `year` | obrigatório, inteiro de 1886 até o ano atual + 1 | `invalid_year` |
| `condition` | `new` ou `used` | `invalid_condition` |
| `mileage` | obrigatório, inteiro de 0 a 2.000.000 km | `invalid_mileage` |
| `price` | obrigatório, maior que 0 e até 100.000.000, até 2 casas decimais | `invalid_price` |
| `is_modified` | obrigatório, verdadeiro ou falso | `invalid_is_modified` |
| `color`, `engine`, `transmission` | opcionais, até 60 | `invalid_<campo>` |
| `description` | opcional, até 2.000 | `invalid_description` |
| `display_name` | 2–60, exigido somente quando a conta ainda não tem anunciante | `invalid_display_name` |

- O backend usa `precondition` com `error_type = "inputerror"` (400) antes de qualquer gravação. **Comparação com null**: em XanoScript, `!=` e `==` são frouxos e tratam `false` e `0` como iguais a `null`; por isso `is_modified` e `mileage`, em que `false` e `0` são válidos, usam `!==`. Defeito encontrado no primeiro POST real da tarefa 3.4 (23/11/2026): `is_modified: false` recebia 400 `invalid_is_modified`, sem gravar nada (a validação vem antes da transação). Os textos são aparados (`trim`), e texto vazio conta como ausente.
- **Ano atual**: calculado no fuso UTC. A sintaxe do filtro será confirmada no MCP na tarefa 2.2.
- **Combinações não validadas**: nenhuma combinação entre campos é presumida (por exemplo, veículo novo com quilometragem), porque o domínio não define essas regras.

### 7. Frontend

- **Módulo e estados**: `revaulte/anuncios.py`, no padrão de `auth.py`:
  - validação pura (`validar_anuncio`) e tradução dos códigos `invalid_*`;
  - `AnunciarState` (formulário, envio, 429);
  - `MeusAnunciosState` (lista e ficha, situações “carregando”, “lista”, “vazia”, “erro”, “nao_encontrado”).
- **Preço**: lido com `ler_valor_br` de `state.py` (formato brasileiro). Quilometragem aceita pontos de milhar.
- **Rotas e proteção**:
  - páginas `/anunciar`, `/meus-anuncios` e `/meus-anuncios/[anuncio_id]`, com `on_load` que reutiliza `AuthState._exigir(rota, None)`;
  - `destino_seguro` passa a aceitar `/anunciar`, `/meus-anuncios` e `/meus-anuncios/<1 a 12 dígitos>`, mantendo a lista fechada.
- **Navegação após o envio**: o envio aceito leva a `/meus-anuncios`, que recarrega a lista e mostra um aviso de sucesso. **Formulário não controlado** (mesmo padrão de `/cadastro`): os dados digitados só vão ao servidor no envio e nunca ficam no estado do Reflex; quando há erro, o próprio navegador mantém os campos preenchidos (decisão de 23/11/2026, plano do frontend aprovado).
- **Campos de escolha**: condição (Novo/Usado) e modificado (Sim/Não) como botões de opção sem opção marcada, para que a escolha seja explícita.
- **Menu**: `ITENS_EM_BREVE` fica só com “Favoritos”. “Anunciar veículo” e “Meus anúncios” viram links para todos. O visitante passa pela proteção da página, que o leva ao login.
- **Configuração**: `REVAULTE_ANUNCIOS_API_URL` em `config.py`, com padrão `https://x8ki-letl-twmt.n7.xano.io/api:revaulte-anuncios`.
- **Rótulos de estado**: `draft` → “Rascunho — aguardando publicação”, `available` → “Publicado”, `sold` → “Vendido”. A ficha de anúncio publicado ou vendido tem link para `/veiculo/<id>`.
- **Erros**:
  - 401 leva ao login;
  - 403 mostra “Acesso restrito”;
  - 404 mostra “Anúncio não encontrado”;
  - 429 pede para aguardar;
  - falha de rede ou status inesperado usa a mensagem genérica com “Tentar novamente”.
- **Navegador**: continua sem acessar o Xano, e o token só sai no cabeçalho das requisições do servidor do Reflex.

### 8. Verificação em três camadas

1. **Testes automatizados** (`frontend/tests/test_anuncios.py`):
   - validação e limites;
   - tradução de erros;
   - preparação das respostas, descartando campos fora da lista;
   - estados com `chamar_xano` simulado (200, 400, 401, 403, 404, 429, rede);
   - `destino_seguro` com as novas rotas;
   - componentes e menu;
   - teste estático dos arquivos `xano/api/anuncios/*.xs` e das tabelas: `auth = "user"`, chamada a `enforce_role`, `status: "draft"` no `POST`, ausência de `user_id`, `seller_id`, `whatsapp` e `contact_` nas saídas, índices únicos de `seller_account`, `seller.xs` sem alteração e nenhum uso de Redis.
2. **Requisições reais** após o envio autorizado, com intervalo de 6 s, parando diante de 429, com duas contas de teste: os cenários de autorização da spec e a comparação do catálogo e do Opala antes e depois.
3. **Navegador**: visitante, Cliente A e Cliente B, em desktop e a 375 px, com o console e a aba de rede (nenhuma requisição direta ao Xano).

### 9. Concorrência e limite de rascunhos (decisões do usuário em 23/11/2026: R1, R2 e opção A)

**R1 — retirada a remoção de anunciantes duplicados.** Uma versão anterior criava o anunciante, reconsultava e apagava o que criou se não fosse o de menor `id`. A revisão mostrou que isso não garantia um anunciante por conta e podia deixar um anúncio órfão. O endpoint só insere: nenhum `db.del`, `db.edit` ou `db.patch`.

**Retirado o `redis.ratelimit` (checagem de 23/11/2026, somente leitura).** A revisão R1/R2 usava `redis.ratelimit` (1 criação por conta a cada 10 s). Motivos da retirada:

- `xano profile me` informa a instância do workspace 169675 como “Free Instance” (pacote `build`), e a página oficial de preços (xano.com/pricing) indica “Data Caching via Redis” somente nos planos Pro e Custom. Rate Limit é uma das funções de Data Caching, então toda criação falharia.
- Mesmo disponível, a garantia era só probabilística: a documentação não diz se a janela começa na primeira requisição ou é alinhada ao relógio, nem o código HTTP da recusa. Com janela alinhada, duas requisições em lados opostos da virada passam juntas; e a trava depende do tempo, não do término da primeira criação.
- Com isso sai também o requisito “Intervalo entre envios” da spec.

**Proteção adotada (opção A).**

- Uma única `db.transaction` envolve contagem de rascunhos, busca do registro `seller_account` da conta, criação do anunciante e do registro (quando não há registro) e gravação do veículo. A documentação oficial descreve a transação sem restrição de plano e sem configurações (“There are no additional settings”): se uma operação de banco falha, as demais são desfeitas.
- **Corrida no primeiro anúncio**: as duas requisições podem não ver registro e criar cada uma um anunciante. A primeira a gravar `seller_account` vence; a gravação da segunda viola o índice único de `user_id`, a transação dela é desfeita (anunciante e veículo dela não ficam gravados) e ela recebe erro. Nenhum registro é apagado depois. Um novo envio da conta encontra o registro e reutiliza o anunciante.
- **Anúncios seguintes**: o registro já existe e só o veículo é gravado. Não há corrida de anunciante.
- A consulta prévia do registro, fora da transação, só decide se o nome de exibição é exigido. Como registros nunca são apagados por este endpoint, a consulta de dentro da transação também o encontra.

**Garantia real e limites residuais.**

- A garantia de um anunciante por conta vem do índice único do banco, não de tempo nem de Redis.
- **Não confirmado por leitura**: que o índice `btree|unique` é aplicado nesta instância e que `db.transaction` desfaz as gravações no plano Free. A tarefa 3.4 confere ambos logo após o envio, antes de qualquer outro teste. Se a transação não desfizer, o pior caso é um anunciante sem registro, sem anúncio e invisível em todo o site (nenhuma consulta o alcança), removível pelo painel com autorização; o veículo da requisição perdedora não é gravado, porque vem depois do registro.
- **Código HTTP da requisição perdedora**: não documentado (provavelmente 500 ou 400 com mensagem de duplicidade). O frontend o trata como erro genérico com “Tentar novamente”; o botão desabilitado durante o envio torna o caso raro.
- **R2 — no máximo 20 rascunhos por conta.** Contagem por `join` com `seller_account.user_id == $auth.id` e `status == "draft"`, dentro da transação e antes de qualquer gravação; com 20 ou mais, 400 `draft_limit_reached`. Publicados e vendidos não contam. Como a transação não tem isolamento configurável (o validador recusa `isolation`), envios simultâneos da mesma conta podem passar o limite por poucos rascunhos; o limite é uma proteção contra abuso, não uma regra exata.

**Alternativas descartadas.**

- `db.transaction` com `isolation = "serializable"`: aparece na documentação do MCP (2.7.1), mas o validador recusa o atributo (“Expecting --> stack”).
- `seller.user_id` com índice único: comportamento com nulos não confirmado (decisão 1).
- Trava por SQL (`db.direct_query` com `pg_advisory_xact_lock`): depende de recurso do plano e de a consulta direta usar a mesma conexão da transação, sem confirmação.
- Sem proteção (só inserção): mais simples, mas não cumpre a regra de um anunciante por conta (opção B, não escolhida).

## Risks / Trade-offs

- [Envio ao Xano afetar dados existentes] → Cópia de segurança com `--records` fora do repositório. Prévia `--dry-run` com a trava usada em `contas-acesso` (decisão 15). Envio parcial com `-i` só de `table/seller_account.xs` e `api/anuncios/*`, sem `--sync`, `--delete` nem `--force`, feito pelo usuário. Comparação do catálogo e do Opala antes e depois.
- [Tabela `seller` alterada por engano] → `seller.xs` fica fora do envio (o arquivo local é idêntico ao da `main`). A prévia deve mostrar somente a tabela nova `seller_account` e o grupo `Anuncios`; qualquer outra diferença interrompe o envio.
- [Caminho diferente do detalhe público no publicado] → O arquivo do catálogo não entra no envio. A divergência fica registrada e não é corrigida nesta Change.
- [Anunciante duplicado em envios simultâneos da mesma conta] → Índice único em `seller_account.user_id` dentro da transação (decisão 9), sem remover registros; botão desabilitado durante o envio.
- [Índice único ou transação sem efeito no plano Free] → Conferido no primeiro teste da tarefa 3.4; se falhar, desligar o grupo `Anuncios` (Migration Plan) antes de qualquer outro uso.
- [Muitos rascunhos por conta] → Limite de 20 (decisão 9), aproximado em envios simultâneos.
- [Limite de 10 requisições/20 s] → Cada página faz `auth/me` e uma chamada de anúncios. 429 tratado com mensagem própria. Testes com intervalo.
- [Rascunhos de teste no banco] → Ficam invisíveis ao público. A remoção é feita pelo painel somente com autorização.
- [Dependência de Changes não arquivadas] → `contas-acesso` e `contato-vendedor` devem ser arquivadas antes desta. O delta de `navegacao-site` substitui o requisito na forma de `contas-acesso`, e arquivar fora de ordem perderia os itens de sessão.
- [Prazo de 27/11/2026] → As tarefas estão ordenadas para que backend e “Meus anúncios” fiquem prontos antes do formulário. Se o prazo apertar, a ficha privada (`/meus-anuncios/<id>`) é a parte que pode ser adiada, com ajuste desta Change.

## Migration Plan

1. Validar os arquivos `.xs` com `xano_validate_xanoscript`.
2. Fazer a cópia de segurança e rodar a prévia protegida. Prévia da opção A (23/11/2026): `xano workspace push -d xano --dry-run -i "table/seller_account.xs" -i "api/anuncios/**"`, com a trava de rede (só 2 requisições, ambas a `/multidoc/dry-run`), 5 de 32 arquivos: `CREATE table seller_account`, `CREATE api_group Anuncios` e 3 endpoints criados; nenhuma atualização nem exclusão, `seller` intocada. Antes da prévia, `pull` do publicado idêntico ao backup e catálogo e Opala byte a byte iguais ao instantâneo; depois, `api:revaulte-anuncios` ainda 404.
3. Apresentar a prévia ao usuário e aguardar a autorização.
4. Envio parcial feito pelo usuário.
5. Nova prévia (“No changes to push”), comparação do catálogo e do Opala e testes reais.

**Reversão**:

- desativar ou excluir o grupo `Anuncios` pelo painel;
- a tabela `seller_account` não é usada por nenhum endpoint público e pode permanecer sem efeito;
- os rascunhos criados ficam invisíveis e podem ser removidos com autorização.

## Open Questions

- Quais contas de teste usar nas requisições e no navegador, e se rascunhos de teste podem ficar no banco até a remoção autorizada. Isso é decidido antes da tarefa 2.4 e não muda as specs.
- O código HTTP que o Xano devolve quando uma gravação viola o índice único (tarefa 3.4), para eventualmente dar uma mensagem própria no frontend.
