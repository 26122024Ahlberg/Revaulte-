# Proposal

## Why

O Revaulte ainda não possui nenhuma funcionalidade implementada: existe apenas um protótipo estático em `frontend-rascunho/`, com veículos escritos diretamente no HTML, e um workspace Xano contendo somente a estrutura inicial de autenticação e logs. O catálogo público é o ponto de partida previsto em `docs/project-overview.md` (seção 11), porque não depende de autenticação e estabelece o conceito de Veículo, do qual as demais funcionalidades dependem.

## What Changes

- Criação de uma página exclusiva de catálogo em Reflex (Python), framework de frontend obrigatório definido pelo professor da disciplina, em uma estrutura definitiva de frontend separada do rascunho.
- A versão da página em HTML, CSS e JavaScript puro, criada antes dessa definição, é preservada como referência de comportamento e identidade visual.
- Listagem de veículos carregada do backend Xano, sem dados de veículos fixos no HTML.
- Exibição, para cada veículo, de informações resumidas: marca, modelo, versão (quando houver), ano, quilometragem, preço e condição (novo ou usado).
- Identificação visual de veículos modificados/preparados com o selo “Modificado”.
- Identificação visual de veículos vendidos com o selo “Vendido”, apresentados como indisponíveis para negociação.
- Exclusão dos veículos em Rascunho já no backend: eles nunca são enviados ao navegador.
- Introdução do conceito de Veículo no backend, apenas com os dados necessários ao catálogo, e de um ponto de acesso público de leitura para a listagem.
- Tratamento dos estados da página: carregando, catálogo vazio e falha ao carregar.

### Fora do escopo

- Login, cadastro e qualquer funcionalidade autenticada.
- Favoritos.
- Simulação de financiamento.
- Filtros, busca e ordenação escolhida pelo usuário.
- Página de detalhes do veículo, configuração original completa e detalhes das modificações.
- Área administrativa e gerenciamento de veículos (cadastro, edição, mudança de estado).
- Gestão definitiva de imagens e galeria de imagens.
- Página inicial, seção de destaques e contato com a loja.
- Paginação da listagem.

O rascunho em `frontend-rascunho/` permanece intacto: serve como referência visual e não é alterado, movido nem completado.

## Capabilities

### New Capabilities

- `catalogo-publico`: listagem pública de veículos em página própria, com dados vindos do backend, incluindo quais veículos são visíveis, quais informações resumidas são exibidas e como veículos modificados e vendidos são identificados.

### Modified Capabilities

Nenhuma. Ainda não existem especificações em `openspec/specs/`.

## Impact

- **Frontend**: nova pasta `frontend/` com o app Reflex da página de catálogo; a versão em HTML/CSS/JS puro fica em `frontend-html/` como referência. Nenhum arquivo de `frontend-rascunho/` é modificado.
- **Backend Xano**: nova tabela de veículos e novo grupo de API público com um endpoint de leitura. As tabelas, funções e endpoints existentes de autenticação e logs não são alterados.
- **Dados**: registros de teste de veículos serão necessários no workspace para verificar a funcionalidade, pois o cadastro pela área administrativa não faz parte desta Change.
- **Segurança**: primeiro endpoint público sem autenticação do projeto; a resposta deve conter somente dados de catálogo e nunca veículos em Rascunho.
- **Dependências**: Reflex (Python), por determinação do professor, o que exige Python 3.11 ou superior no ambiente de desenvolvimento. Nenhuma outra tecnologia nova.
- **Documentação**: o trecho “Workspace Xano” de `docs/project-overview.md` foi atualizado na revisão desta Change para registrar que o workspace já está conectado e sincronizado em `xano/`.
- **Repositório**: a pasta `xano/` passa a ser versionada no Git, e um `.gitignore` na raiz exclui arquivos de credenciais e de ambiente.
