# Revaulte — Roteiro de testes de Favoritos

Roteiro manual da Change `favoritos`. Complementa os testes automáticos (`frontend/tests/test_favoritos.py`), que simulam o Xano.

## Antes de começar

- **Estado do Xano (24/11/2026)**: `favorite` e o grupo `Favoritos` já estão publicados e verificados (tabela vazia, 3 endpoints, sem token = 401). Cópias de segurança em `~/xano-backups/2026-11-24-antes-favoritos` e `-depois-favoritos`.
- **Dados reais**: os testes abaixo gravam favoritos reais no Xano. Use somente as contas de teste A e B e **termine pela seção 6 (limpeza)**, deixando `favorite` vazia.
- **Ordem recomendada**: 1 → 2 → 3 → 4 (4 só com autorização para mudar estados no painel) → 5 → 6.
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

## 6. Limpeza e registro

> **Atenção (26/11/2026):** a tabela `favorite` tem hoje **3 registros** (contas 3 e 4), que devem ser **preservados**. Não execute as linhas 6.1 e 6.2 nem remova favoritos existentes sem nova autorização. O estado “tabela vazia” citado neste roteiro é o de 24/11/2026.

| # | Ação | Resultado esperado |
| --- | --- | --- |
| 6.1 | Com A e depois com B, abrir `/favoritos` e usar “Remover dos favoritos” em cada cartão | As duas listas ficam vazias |
| 6.2 | No painel do Xano, conferir a tabela `favorite` | 0 registros (se sobrar algum, remover só os das contas de teste, com autorização) |
| 6.3 | Conferir `/estoque` | Seis veículos; `/veiculo/7` continua 404 |
| 6.4 | Registrar cada linha como OK ou falha, com data, em `openspec/changes/favoritos/design.md` | Resultado arquivado com a Change |

## Verificação por API (opcional, com tokens obtidos pelo login do site)

Nunca grave tokens em arquivos nem em histórico compartilhado. Com 6 s entre requisições:

- Sem `Authorization`: `GET /favoritos`, `POST /favoritos/1` e `DELETE /favoritos/1` respondem 401 (já confirmado em 24/11/2026).
- Com o token de A: `POST /favoritos/1` → 200 `{"vehicle_id":1,"favorited":true}`; repetir → 200 e um único registro; `GET /favoritos` → `[{"vehicle_id":1,...}]`.
- Com o token de B: `GET /favoritos` → `[]`; `POST /favoritos/7` e `POST /favoritos/99999` → 404 iguais.

## Registro de execução

| Data | Resultado |
| --- | --- |
| 24/11/2026 | Execução manual no navegador pelos Clientes A e B (relato e capturas de tela da equipe): favoritar, listar por conta e remover; ao final, as listas de A e de B ficaram vazias e a tabela `favorite` no Xano tinha 0 registros |

**Não verificado:** os registros de `favorite` não foram inspecionados no banco enquanto existiam, então os pares `user_id` + `vehicle_id` e a ausência de duplicatas não foram confirmados diretamente no banco; o índice único não foi testado em execução nem em concorrência. As linhas 3.1 a 3.5 e 4.1 e 4.2 deste roteiro (API com tokens, veículo Vendido ou em Rascunho) não foram registradas como executadas.
