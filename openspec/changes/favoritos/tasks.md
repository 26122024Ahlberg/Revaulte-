# Tasks

> **Situação (24/11/2026):** implementação e testes locais concluídos (410 testes, `reflex compile --dry`, `xano_validate_xanoscript` com 37 arquivos válidos e `openspec validate favoritos --strict`). Nada foi enviado ao Xano nem ao GitHub.

## 1. Backend local (sem envio ao Xano)
- [x] 1.1 Criar `xano/table/favorite.xs` (índice único `user_id`+`vehicle_id`); validar com `xano_validate_xanoscript`
- [x] 1.2 Criar o grupo `Favoritos` e os endpoints `GET /favoritos`, `POST /favoritos/{vehicle_id}`, `DELETE /favoritos/{vehicle_id}`; validar
- [x] 1.3 Teste estático dos `.xs` (`auth`, `enforce_role` primeiro, sem `user_id` na entrada, só veículos públicos)

## 2. Frontend
- [x] 2.1 `config.py`: `favoritos_api_url()`; `favoritos.py`: funções puras e `FavoritosState`
- [x] 2.2 Botão na página do veículo e página `/favoritos`; rota em `destino_seguro`; limpeza ao sair
- [x] 2.3 Menu: “Favoritos” como link; atualizar testes de menu
- [x] 2.4 Estilos em `styles.css`

## 3. Verificação
- [x] 3.1 Suíte completa, `reflex compile --dry` e `openspec validate favoritos --strict`
- [x] 3.2 Roteiro `docs/testes-favoritos.md` criado (24/11/2026); **a execução real no navegador depende do envio ao Xano, que ainda não foi autorizado**

## Workflow follow-up
- Envio ao Xano, push e archive somente com autorização.
