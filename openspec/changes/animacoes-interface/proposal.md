# Proposal

## Why

Para a apresentação, a interface da Revaulte precisa transmitir acabamento premium. Transições e microinterações discretas reforçam a identidade, desde que não comprometam desempenho, responsividade e acessibilidade. Esta Change vem por último, depois que os fluxos principais funcionarem.

## What Changes

- Entrada suave das seções e dos cartões (opacidade e deslocamento curtos).
- Microinterações de foco e passagem do cursor em cartões, botões e itens do menu.
- Indicação de carregamento animada no lugar do texto estático, mantendo o texto para tecnologias assistivas.
- Desativação das animações para quem prefere movimento reduzido.

### Fora do escopo

- Bibliotecas de animação, JavaScript próprio, vídeo, paralaxe e carrosséis.
- Mudanças de conteúdo, rotas ou backend.

## Capabilities

### New Capabilities

- `animacoes-interface`: regras de movimento da interface pública, incluindo preferência por movimento reduzido e foco visível.

### Modified Capabilities

Nenhuma.

## Impact

- **Frontend Reflex**: principalmente `frontend/assets/styles.css`; classes adicionais em `components.py` quando necessário.
- **Backend Xano**: nenhum.
- **Dependências**: aplicar depois das demais Changes do MVP.
