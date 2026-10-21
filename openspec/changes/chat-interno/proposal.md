# Proposal

## Why

No marketplace, comprador e anunciante precisam negociar sem depender só de canais externos, e a conversa precisa ficar ligada ao anúncio. Um chat interno mantém o histórico na Revaulte e evita expor o número de telefone de quem não quer.

Esta Change é **somente planejamento**. Ela depende de cadastro, login e anunciantes, que ainda não existem, e não será implementada antes da apresentação.

## What Changes

- Conversa entre um comprador autenticado e o anunciante, sempre associada a um anúncio.
- Mensagens de texto com data e hora, histórico da conversa e lista “Minhas conversas”.
- Indicação de mensagens não lidas e notificações dentro do site.
- Acesso a cada conversa restrito aos dois participantes, verificado no backend.

### Fora do escopo

- Envio de arquivos, áudio ou imagens; notificações por e-mail, SMS ou push.
- Moderação automática, denúncia e bloqueio (avaliar em Change própria).
- Pagamentos, propostas formais e reservas pelo chat.

## Capabilities

### New Capabilities

- `chat-interno`: conversas entre comprador e anunciante vinculadas a anúncios, com histórico, não lidas e controle de acesso.

### Modified Capabilities

Nenhuma.

## Impact

- **Backend Xano** (somente após autorização): tabelas de conversa e mensagem, endpoints autenticados, regras de autorização por participante; avaliar o recurso de tempo real do Xano antes de decidir entre tempo real e consulta periódica.
- **Frontend Reflex**: botão “Enviar mensagem” na página do veículo, páginas “Minhas conversas” e da conversa, indicador de não lidas no menu da conta.
- **Domínio e documentação**: conceitos Conversa e Mensagem em `docs/domain-model.md`.
- **Dependências**: cadastro e login (Change futura), `contato-vendedor` (Anunciante) e `detalhes-veiculo`.
