# Revaulte — Roteiro de testes de Favoritos

Roteiro manual da Change `favoritos`. Complementa os testes automáticos (`frontend/tests/test_favoritos.py`), que simulam o Xano.

## Antes de começar

- **Pré-requisito**: os arquivos `xano/table/favorite.xs` e `xano/api/favoritos/*` precisam estar publicados no Xano. Isso só deve ser feito com autorização da equipe, com cópia de segurança antes e prévia `--dry-run` (ver `design.md` da Change). Sem o envio, o site mostra a mensagem genérica de erro nas ações de favoritos.
- **Dados fictícios**: use contas de teste (`example.com`). Não registre senhas ou tokens em arquivos.
- **Limite do Xano**: 10 requisições a cada 20 s; faça uma ação por vez.
- **Ambiente**: `reflex run` em `frontend/`; site em `http://localhost:3000/`. Contas: Cliente A e Cliente B.

## 1. Visitante

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 1.1 | Abrir ☰ | “Favoritos” é link (não “Em breve”) |
| 1.2 | Acionar “Favoritos” | Vai para `/entrar?proximo=/favoritos` |
| 1.3 | Abrir `/veiculo/1` e acionar “Favoritar” | Vai para `/entrar?proximo=/veiculo/1`; nada é gravado |

## 2. Cliente A

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 2.1 | Entrar e abrir `/favoritos` | “Você ainda não favoritou nenhum veículo” e link “Ver o estoque” |
| 2.2 | Abrir `/veiculo/1` | Botão “Favoritar” |
| 2.3 | Acionar “Favoritar” | Botão vira “Remover dos favoritos”; sem recarregar a página |
| 2.4 | Recarregar a página | Botão continua “Remover dos favoritos” |
| 2.5 | Favoritar também o veículo 2 e abrir `/favoritos` | Dois cartões, o veículo 2 primeiro; cada um com “Remover dos favoritos” |
| 2.6 | Clicar no cartão | Abre a página do veículo |
| 2.7 | Em `/favoritos`, “Remover dos favoritos” no veículo 1 | O cartão some; o veículo 2 continua |
| 2.8 | Remover o último | Mensagem de lista vazia |
| 2.9 | 📱 Repetir 2.3 e 2.5 em 375 px | Sem rolagem horizontal; botões na largura útil |
| 2.10 | Sair | Volta à Home; `/favoritos` leva ao login |

## 3. Isolamento e autorização

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 3.1 | Cliente A favorita o veículo 1; entrar como B e abrir `/favoritos` | Lista vazia para B |
| 3.2 | Sem token, `GET`, `POST` e `DELETE` do grupo `Favoritos` | 401 |
| 3.3 | Com token, `POST /favoritos/<id de Rascunho>` e `POST /favoritos/99999` | 404 idêntico |
| 3.4 | `POST` duas vezes no mesmo veículo | Duas respostas 200; `GET` lista um só id |
| 3.5 | `DELETE` de veículo não favoritado | 200 |

## 4. Veículo que muda de estado

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 4.1 | Favoritar um veículo; a equipe marca como Vendido | Continua em `/favoritos` com o selo “Vendido” |
| 4.2 | A equipe volta o veículo a Rascunho | Deixa de aparecer em `/favoritos` (o registro permanece no Xano) |

## 5. Preservação

Conferir que `/estoque` ainda lista os seis veículos, o anúncio 7 continua em Rascunho (404 em `/veiculo/7`) e o Opala mantém o contato por WhatsApp.
