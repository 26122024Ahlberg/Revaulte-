# Proposal

## Why

A Revaulte já tem contas de Cliente (Change `contas-acesso`), mas os anúncios ainda são cadastrados somente pela equipe no painel do Xano, e no menu “Anunciar veículo” e “Meus anúncios” aparecem como “Em breve”. Com a entrega prorrogada para 27/11/2026, esta Change permite que o Cliente autenticado envie o próprio anúncio e acompanhe seus anúncios. É o passo previsto no modelo de domínio: “futuramente, um Anunciante estará associado a uma Conta” (conceito aprovado em 27/10/2026).

## What Changes

- Vínculo seguro entre conta, anunciante e veículo. O anunciante passa a poder pertencer a uma conta (no máximo um anunciante por conta, garantido por um registro com índice único), e o veículo continua ligado ao anunciante. O vínculo é sempre definido pelo backend a partir da sessão, nunca por dados enviados pelo navegador.
- **Anunciar veículo** (`/anunciar`): formulário para o Cliente autenticado enviar marca, modelo, versão, ano, condição, quilometragem, preço, indicação de modificado, cor, motorização, câmbio, descrição e, no primeiro anúncio, o nome de exibição do anunciante.
- Todo anúncio enviado pelo site nasce como **Rascunho**: fica invisível no catálogo público e só é publicado (Disponível) pela equipe, no painel do Xano. Ninguém escolhe o estado pelo site.
- **Meus anúncios** (`/meus-anuncios`): lista somente os anúncios da própria conta, com o estado de cada um. A página `/meus-anuncios/<id>` mostra a ficha completa de um anúncio próprio, inclusive em Rascunho.
- Autorização no backend: sem sessão, a requisição é recusada (401). Um anúncio de outra conta, um anúncio da equipe e um identificador inexistente recebem a mesma resposta 404. Nenhum endpoint desta Change altera anúncios existentes.
- Um anúncio de Cliente nasce sem contato autorizado, então a página pública não exibe WhatsApp para ele.
- Menu “Minha conta”: “Anunciar veículo” e “Meus anúncios” deixam de ser “Em breve” e passam a ser links. “Favoritos” continua “Em breve”.
- Preservação: o catálogo público, os seis veículos atuais, as contas existentes e o contato autorizado do Opala não são alterados.

Fora do escopo:

- edição e exclusão de anúncio pelo Cliente (Change futura);
- envio de fotos (o anúncio usa a imagem provisória);
- modificações por área no formulário;
- contato por WhatsApp de anunciantes cadastrados pelo site;
- moderação ou publicação pelo `/admin`;
- favoritos e chat interno.

## Capabilities

### New Capabilities

- `anuncios-cliente`: anúncios enviados por Clientes autenticados: vínculo conta → anunciante → veículo, criação sempre em Rascunho, consulta privada dos próprios anúncios, autorização no backend e preservação do catálogo público.

### Modified Capabilities

- `navegacao-site`: o requisito “Menu da conta” (e o “Menu em tela estreita”, que repete os itens) passa a oferecer “Anunciar veículo” e “Meus anúncios” como links. O delta parte da versão do requisito definida pela Change `contas-acesso`, ainda não arquivada.

## Impact

- **Xano** (envio somente com autorização, em etapa própria):
  - nova tabela `seller_account` (registro conta → anunciante, com índices únicos em `user_id` e em `seller_id`); a tabela `seller` não muda;
  - novo grupo de API `Anuncios` (canonical `revaulte-anuncios`) com `POST /anuncios`, `GET /anuncios` e `GET /anuncios/{vehicle_id}`, todos com `auth = "user"`;
  - nenhuma alteração em `seller`, `vehicle`, `vehicle_modification`, `user` nem nos endpoints do catálogo ou de autenticação.
- **Dados**: nenhum registro existente é alterado. Os rascunhos de teste criados na verificação só são removidos com autorização.
- **Frontend Reflex**:
  - novo módulo `revaulte/anuncios.py`;
  - páginas `/anunciar`, `/meus-anuncios` e `/meus-anuncios/[anuncio_id]`;
  - `config.py` (`REVAULTE_ANUNCIOS_API_URL`);
  - `auth.py` (rotas protegidas e destinos seguros do `?proximo=`);
  - `components.py` (menu);
  - `styles.css`;
  - novos testes em `frontend/tests/`.
- **Documentação**: `docs/domain-model.md` (Anunciante e limites), `docs/project-overview.md`, `README.md` e `frontend/README.md`.
- **Dependências**: nenhuma nova. Depende de `contas-acesso` (sessão, `auth/me`, `enforce_role`) e de `contato-vendedor` (tabela `seller`); ver `design.md`.
