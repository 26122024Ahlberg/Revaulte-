# Revaulte — Roteiro de testes de Anunciar veículo e Meus anúncios

Roteiro manual da Change `anuncios-cliente`. Complementa os testes automáticos (`frontend/tests/test_anuncios.py` e `test_xano_anuncios.py`).

## Antes de começar

- O backend (`seller_account`, grupo `Anuncios`) já está publicado no Xano. Cada criação grava um Rascunho real: use dados fictícios e liste os rascunhos de teste ao final (a remoção é feita pelo painel do Xano, com autorização).
- Limite do Xano: 10 requisições a cada 20 s.
- Contas: Cliente A e Cliente B (fictícias).

## 1. Visitante

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 1.1 | Abrir `/anunciar` | Vai para `/entrar?proximo=/anunciar` |
| 1.2 | Abrir `/meus-anuncios` e `/meus-anuncios/7` | Vai para o login, voltando à mesma página depois |
| 1.3 | Menu ☰ | “Anunciar veículo” e “Meus anúncios” são links |

## 2. Cliente A

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 2.1 | Abrir `/meus-anuncios` sem anúncios | Mensagem de lista vazia e link “Anunciar veículo” |
| 2.2 | Em `/anunciar`, enviar vazio | Mensagem do primeiro campo inválido; nada é enviado |
| 2.3 | Preço ou ano fora dos limites | Mensagem própria; dados digitados mantidos |
| 2.4 | Primeiro anúncio válido, com nome de exibição | Vai para `/meus-anuncios` com o aviso de envio; o anúncio aparece como “Rascunho” |
| 2.5 | Segundo anúncio | O nome de exibição não é pedido; anunciante mostrado só para leitura |
| 2.6 | “Ver detalhes” de um anúncio | Ficha completa, sem editar nem excluir; sem link público (Rascunho) |
| 2.7 | `/veiculo/<id do rascunho>` e `/estoque` | 404 / o rascunho não aparece no catálogo |
| 2.8 | 📱 Repetir 2.4 e 2.6 em 375 px | Sem rolagem horizontal |

## 3. Cliente B e autorização

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 3.1 | B abre `/meus-anuncios` | Não vê os anúncios de A |
| 3.2 | B abre `/meus-anuncios/<id de A>`, `/meus-anuncios/1` (Opala) e um id inexistente | “Anúncio não encontrado”, igual nos três |
| 3.3 | Sem token, `GET` e `POST` de `Anuncios` | 401 |
| 3.4 | `POST` com `status`, `seller_id` ou `user_id` no corpo | Criado em Rascunho, para a conta do token |

## 4. Preservação

O catálogo continua com os seis veículos, o contato do Opala permanece e `/veiculo/7` continua 404 até a equipe publicar.
