# Proposal

## Why

Hoje a seção “Veículos em destaque” da Home mostra os três veículos Disponíveis cadastrados mais recentemente. Com a expansão do estoque demonstrativo (seis veículos novos, gravados com a data real de cadastro), os três mais recentes passariam a ser os novos, e os veículos 4, 5 e 6, que hoje estão em destaque, sairiam da Home. A equipe decidiu manter esses três em destaque **sem alterar datas de cadastro**.

## What Changes

- A Home passa a priorizar um conjunto editorial de destaques, os veículos de identificadores **4, 5 e 6**, desde que estejam Disponíveis e presentes no catálogo público.
- Quando algum deles estiver Vendido ou ausente, as vagas restantes (até três no total) são completadas com os Disponíveis cadastrados mais recentemente que não sejam do conjunto editorial.
- Os destaques editoriais aparecem na ordem em que o catálogo os devolve (do mais recente para o mais antigo), isto é, na mesma ordem de hoje: 6, 5 e 4.
- Sem nenhum veículo do conjunto editorial no catálogo, o comportamento atual é mantido integralmente (três Disponíveis mais recentes).
- Não há mudança no Xano, no esquema, na API pública nem na ordenação das páginas de Estoque, Usados e Modificados.

Fora do escopo: campo de destaque no banco, tela administrativa para escolher destaques, qualquer alteração de datas de cadastro.

## Capabilities

### Modified Capabilities

- `pagina-inicial`: requisito “Veículos em destaque”.

## Impact

- `frontend/revaulte/state.py` (recorte `destaques`), `frontend/revaulte/components.py` (comentário), `frontend/tests/test_preparacao.py`.
- Documentação: `docs/domain-model.md`, `docs/project-overview.md`, `docs/expansao-estoque.md`.
