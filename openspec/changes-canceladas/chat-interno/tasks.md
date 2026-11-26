# Tasks

## 1. Pré-requisitos (planejamento; nada a implementar agora)

- [ ] 1.1 Confirmar com o usuário que cadastro, login e `contato-vendedor` foram concluídos e autorizar o início desta Change; verificar a aprovação
- [ ] 1.2 Consultar no Xano Developer MCP autenticação, autorização por registro e recursos de tempo real; registrar em um `design.md` a escolha entre tempo real e consulta periódica, o tamanho máximo da mensagem e a retenção do histórico; verificar a revisão do usuário

## 2. Backend (somente após autorização)

- [ ] 2.1 Criar as tabelas de conversa e mensagem e os endpoints autenticados; verificar com `xano_validate_xanoscript` e por requisições: participante lê e envia, terceiro e visitante são recusados, vendido não aceita nova conversa

## 3. Frontend

- [ ] 3.1 Implementar “Enviar mensagem”, “Minhas conversas”, a página da conversa e o indicador de não lidas; verificar com testes em `frontend/tests/` e no navegador cada cenário da spec

## 4. Verificação

- [ ] 4.1 Executar os testes, `reflex compile` e `openspec validate chat-interno --strict`; verificar que passam
