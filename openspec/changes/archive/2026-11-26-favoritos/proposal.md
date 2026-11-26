# Proposal

## Why

O modelo de domínio prevê que o Cliente autenticado possa favoritar veículos para consulta posterior (`docs/domain-model.md`, “Favorito”), e o menu “Minha conta” ainda mostra “Favoritos” como “Em breve”. Esta Change conclui essa funcionalidade antes da entrega de 27/11/2026.

## What Changes

- **Favoritar** (página do veículo `/veiculo/<id>`): botão “Favoritar” / “Remover dos favoritos” para veículos do catálogo público (Disponível ou Vendido). Visitante sem sessão é levado a `/entrar?proximo=/veiculo/<id>`.
- **Favoritos** (`/favoritos`): lista, para o Cliente autenticado, os veículos que ele favoritou, com o mesmo cartão do catálogo e a ação “Remover dos favoritos”.
- **Backend** (grupo `Favoritos`, canonical `revaulte-favoritos`): tabela `favorite` (conta + veículo, par único) e endpoints `GET /favoritos` (ids dos veículos favoritados), `POST /favoritos/{vehicle_id}` e `DELETE /favoritos/{vehicle_id}`, todos com `auth = "user"` e `enforce_role`. A conta vem sempre do token.
- Comportamento definido para o caso em aberto do domínio: veículo que deixa de ser público (Rascunho) não é favoritável e não aparece em `/favoritos`; veículo Vendido continua favoritável e aparece com o selo “Vendido”.
- Menu “Minha conta”: “Favoritos” deixa de ser “Em breve” e vira link para `/favoritos`.
- Preservação: catálogo, seis veículos, contas, anúncio 7 e contato do Opala não são alterados.

Fora do escopo: notificações de mudança de estado, compartilhamento de lista, contagem pública de favoritos, simulações salvas e chat.

## Capabilities

### New Capabilities

- `favoritos`: favoritar, desfavoritar e consultar favoritos do Cliente.

### Modified Capabilities

- `navegacao-site`: item “Favoritos” do menu passa a ser link.

## Impact

- `xano/table/favorite.xs`, `xano/api/favoritos/*` (arquivos locais; **envio ao Xano somente com autorização**).
- `frontend/revaulte/favoritos.py`, `components.py`, `auth.py`, `revaulte.py`, `config.py`, `styles.css`, testes.
- Documentação: `docs/domain-model.md`, `README.md`, `docs/testes-favoritos.md`.
