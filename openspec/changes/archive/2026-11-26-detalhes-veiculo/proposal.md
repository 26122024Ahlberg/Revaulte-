# Proposal

## Why

O visitante vê no catálogo apenas um resumo de cada veículo e não tem como consultar mais nada. Para um marketplace especializado em clássicos, esportivos e preparados, a página individual, com a configuração original e as modificações, é o ponto central do produto (ver `docs/project-overview.md`, seção 6).

## What Changes

- Página individual em `/veiculo/<id>`, pública, com foto principal (com imagem provisória), título, ano, quilometragem, condição, preço e selos “Modificado” e “Vendido”.
- Informações técnicas da configuração original (cor, motorização, câmbio) e descrição, exibidas quando cadastradas.
- Lista de modificações por área, exibida quando cadastrada, sem presumir regularização.
- Botão “Voltar ao estoque” e botão “Tenho interesse” demonstrativo, que apenas informa que o contato com o anunciante ainda não está disponível; ausente para veículo vendido.
- Cartões do catálogo e dos destaques passam a levar à página do veículo.
- Tratamento de identificador inexistente, inválido ou de veículo em Rascunho como “veículo não encontrado”, e de falha do backend com opção de tentar novamente.
- Backend (execução depende de autorização do usuário após revisão desta proposta): campos opcionais `color`, `engine`, `transmission` e `description` em `vehicle`, nova tabela `vehicle_modification` e endpoint público `GET /vehicles/{vehicle_id}`.
- Entrega em duas etapas: primeiro a página usando a listagem pública atual (sem dados técnicos e modificações); depois a troca para o novo endpoint, quando autorizado.

### Fora do escopo

- Galeria com várias imagens, upload de imagens, favoritos, simulação de financiamento e contato real com o anunciante.
- Situação de regularização das modificações (não há definição no domínio).
- Cadastro ou edição de veículos e modificações (área administrativa).

## Capabilities

### New Capabilities

- `detalhes-veiculo`: página pública de um veículo, acesso a partir dos cartões, tratamento de não encontrado e endpoint público de detalhe.

### Modified Capabilities

Nenhuma. Tornar os cartões clicáveis acrescenta comportamento sem alterar requisitos de `catalogo-publico`.

## Impact

- **Frontend Reflex**: rota dinâmica, novo estado de detalhe, componentes da página e cartões como links.
- **Backend Xano** (somente após autorização): alteração aditiva na tabela `vehicle`, nova tabela `vehicle_modification`, novo endpoint no grupo `Catalog`; `GET /vehicles` não muda.
- **Dados de teste**: preencher dados técnicos e modificações de alguns veículos pelo painel do Xano.
- **Documentação**: registrar em `docs/domain-model.md` as áreas de modificação adotadas e que a regularização não é modelada nesta etapa.
- **Dependências**: depois de `navegacao-principal` (rota `/estoque`).
